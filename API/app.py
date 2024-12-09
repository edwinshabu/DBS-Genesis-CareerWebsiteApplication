import base64
from datetime import datetime, timedelta
from flask import session
from flask import Flask, request, jsonify
from requests import Session
from authentication import Operations
from alloperations import AllOperations, Employer


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem
session = Session()
user_sessions = {}
SESSION_TIMEOUT = 3000

# Login and Registeration #####################################

@app.route('/Register', methods=['POST'])
def register():
    data = request.form
    output = Operations.Register(data)
    return output

@app.route('/Login', methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    
    auth, status = Operations.Authentication(username, password)
    if status == 200:
        output = Operations.Login(username, password)
        session_id = f"session_{username}"
        user_sessions[session_id] = {
            "username": username,
            "password" : password,
            "start_time": datetime.now(),
            "expiry_time": datetime.now() + timedelta(minutes=SESSION_TIMEOUT)
        }
        return output
    else:
        return jsonify({"message": auth}), status


@app.route('/Signout', methods=['GET'])
def Signout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        session_id = f"session_{username}"
        if session_id in user_sessions:
            del user_sessions[session_id]
            return jsonify({"message":"Logged Out"}), 200
        else:
            return jsonify({"message": "Logged Out"}), 200
    else:
        return jsonify({"message": "Logged Out"}), 200


@app.route('/ListAllUsers', methods=['GET'])
def listallusers():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        auth = Operations.Authentication(username, password)
        if auth:
            output = AllOperations.ListAllUsers()
            return jsonify(output)
        else:
            return jsonify({"message": "User is not registered."}), 404
    else:
        return jsonify({"timeout": "Session Timeout"}), 401


@app.route('/DeleteUser', methods=['DELETE'])
def Delete_user():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        auth = Operations.Authentication(username, password)
        if auth:
            data = request.get_json()
            if not data or 'username' not in data:
                return jsonify({"message": "Username is required"}), 400

            username = data['username']

            # Call the function to delete the user
            result = AllOperations.DeleteUser(username)

            if "deleted successfully" in result:
                return jsonify({"message": result}), 200
            else:
                return jsonify({"message": result}), 404
        else:
            return jsonify({"message": "User is not registered."}), 404
    else:
        return jsonify({"timeout": "Session Timeout"}), 401
    
    
@app.route('/ForgotPassword', methods=['POST'])
def ForgotPassword():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"message": "Username is required"}), 400
    if not data or 'email' not in data:
        return jsonify({"message": "EmailId is required"}), 400

    username = data['username']
    email = data['email']

    result, status = Operations.ForgotPassword(username, email)
    return jsonify({"message":result}),status
    
@app.route('/CreateJob', methods=['POST'])
def CreateJob():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        check, stats = Employer.CheckEmployer(username, password)
        if stats != 200:
            return jsonify({"message":f'{check}'}),stats
        if check:
            auth, s = Operations.Authentication(username, password)
            if s == 200:
                data = request.get_json()  # Get the data from the request body
                result, status = Employer.CreateJob(data, username, password)  # Call the CreateJob method from Employer
                return jsonify({"message" : f'{result}'}), status
            else:
                return jsonify({"message": f"{auth}"}), s
        else:
            return jsonify({"message": "Not authorized except Employer."}), 401
    else:
        return jsonify({"timeout": "Session Timeout"}), 401
    
@app.route('/ApplyApplication', methods=['POST'])
def ApplyJob():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        check, s = Employer.CheckEmployer(username, password)
        if s != 200:
            return jsonify({"message" : f'check'}), s

        if not check:
            data = request.get_json()
            JobId = data.get('JobId')
            if JobId:
                pass
            else:
                return jsonify({"message": "JobId is missing in the request body"}), 400
            res, status = AllOperations.ApplyApplication(username, password, JobId)
            if status != 200:
                return jsonify({"message":f'{res}'}), status
            
            return jsonify({"message": f"{res}"}), status
            
        else:
            return jsonify({"message": "Not authorized for Employer."}), 401
    else:
        return jsonify({"message": "Session Timeout"}), 401



@app.route('/UpdateApplication', methods=['POST'])
def UpdateApplication():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        check, status = Employer.CheckEmployer(username, password)
        if status == 200:
            auth, stat = Operations.Authentication(username, password)
            if stat == 200: 
                data = request.get_json()
                result, stats = Employer.UpdateApplication(data,username, password)
                return jsonify({"message": f'{result}'}), stats
            else:
                return jsonify({"message": f"{auth}"}), stat
        else:
            return jsonify({"message": f"{check}"}), status
    else:
        return jsonify({"timeout": "Session Timeout"}), 401
        
@app.route('/ShowApplications', methods=['GET'])
def ShowApplications():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        auth, status = Operations.Authentication(username, password)
        if status == 200:
            result, stat = Employer.ShowAllApplications(username, password)  # Call the CreateJob method from Employer
            
            return jsonify(result), stat
        else:
            return jsonify({"message": f"{auth}"}), status
    else:
        return jsonify({"timeout": "Session Timeout"}), 401
        

@app.route('/ShowSpecificApplications', methods=['GET'])
def ShowSpecificApplications():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        auth, status = Operations.Authentication(username, password)
        if status == 200:
            result, s = Employer.ShowSpecificApplications(username, password)  # Call the CreateJob method from Employer
            
            return result, s
        else:
            return jsonify({"message": f"{auth}"}), status
    else:
        return jsonify({"timeout": "Session Timeout"}), 401
        
@app.route('/ShowJobs', methods=['GET'])
def ShowJobs():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_username = auth_header.split(" ")[1]
        username = base64.b64decode(base64_username).decode("utf-8")
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    password = AllOperations.CheckSession(username, user_sessions)
    if password:
        auth, status = Operations.Authentication(username, password)
        if status == 200:
            result = Employer.ShowJobs(username, password)  # Call the CreateJob method from Employer
            return result

        else:
            return auth, status
    else:
        return jsonify({"message": "Session Timeout"}), 401
        
@app.route('/ListOrganization',methods=['GET'])
def ListOrganization():
    result = AllOperations.ShowOrganizations()
    return result

@app.route('/ShowUserType',methods=['GET'])
def ListUserTypes():
    result = AllOperations.ShowUserTypes()
    return result





    
if __name__ == '__main__':
    app.run(debug=True, port=8081)
