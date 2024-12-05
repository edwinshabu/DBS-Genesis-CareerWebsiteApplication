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
SESSION_TIMEOUT = 30


# Login and Registeration #####################################

@app.route('/Register', methods=['POST'])
def register():
    data = request.form
    output = Operations.Register(data)
    return output
    
# @app.route('/Login', methods=['POST'])
# def login():
#     data = request.get_json()
#     output = Operations.Login(data)
#     return output

@app.route('/Login', methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Basic "):
        base64_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
    else:
        return jsonify({"message": "Authentication header is missing."}), 400
    
    output = Operations.Login(username, password)
    session_id = f"session_{username}"
    user_sessions[session_id] = {
        "username": username,
        "start_time": datetime.now(),
        "expiry_time": datetime.now() + timedelta(minutes=SESSION_TIMEOUT)
    }
    return output


    

@app.route('/ListAllUsers', methods=['GET'])
def listallusers():
    output = AllOperations.ListAllUsers()
    return jsonify(output)

@app.route('/DeleteUser', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Username is required"}), 400

    username = data['username']

    # Call the function to delete the user
    result = AllOperations.DeleteUser(username)

    if "deleted successfully" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": result}), 404
    
@app.route('/ForgotPassword', methods=['POST'])
def ForgotPassword():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Username is required"}), 400
    if not data or 'email' not in data:
        return jsonify({"error": "EmailId is required"}), 400

    username = data['username']
    email = data['email']

    result = Operations.ForgotPassword(username, email)
    if result[1] == 200:
        return jsonify({"message": "Password sent to your registered Email."}), 200
    elif result[1] == 404:
        return jsonify({"message":"Either the Username or the Email Address is not registered."}), 404
    else:
        return jsonify({"error": "Unknow Error, Please contact Admin."}), 500
    
@app.route('/Employer/CreateJob', methods=['POST'])
def CreateJob():
    data = request.get_json()  # Get the data from the request body
    result = Employer.CreateJob(data)  # Call the CreateJob method from Employer
    
    if isinstance(result, tuple) and len(result) == 2:
        return result[0], result[1]
    else:
        return jsonify({"error": "Unexpected result format"}), 500
    
@app.route('/Employer/ShowApplications', methods=['GET'])
def ShowApplications():
    result = Employer.ShowApplications()  # Call the CreateJob method from Employer
    
    if isinstance(result, tuple) and len(result) == 2:
        return result[0], result[1]
    else:
        return jsonify({"error": "Unexpected result format"}), 500
    
@app.route('/ShowJobs', methods=['GET'])
def ShowJobs():
    result = Employer.ShowJobs()  # Call the CreateJob method from Employer
    
    if result:
        return result
    else:
        return jsonify({"error": "Unexpected result format"}), 500
    
@app.route('/ListOrganization',methods=['GET'])
def ListOrg():
    result = AllOperations.ShowOrganizations()
    return result

@app.route('/ShowUserType',methods=['GET'])
def ListOrganization():
    result = AllOperations.ShowUserTypes()
    return result





    
if __name__ == '__main__':
    app.run(debug=True, port=8081)
