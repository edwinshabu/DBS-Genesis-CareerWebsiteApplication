import base64
from datetime import datetime, timedelta  
import requests
from flask import Flask, redirect, request, render_template

app = Flask(__name__)

app.config['SECRET_KEY'] = 'genesiscareer'  
app.config['SESSION_TYPE'] = 'filesystem'
session = requests.Session()
user_sessions = {}
SESSION_TIMEOUT = 3000

def CheckSession(username, user_sessions):
    session_id = f"session_{username}"
    if session_id not in user_sessions:
        return False
    
    session = user_sessions[session_id]
    if datetime.now() > session["expiry_time"]:
        del user_sessions[session_id]
        return False    
    return True


API_URL = "http://127.0.0.1:8081/"

@app.route('/')
def index():
    return render_template('index.html', popup_message=None)

@app.route('/employer-dash')
def empdash():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")

    return render_template('employer-dash.html', popup_message=None)

@app.route('/user-dash')
def userdash():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    return render_template('user-dash.html', popup_message=None)

@app.route('/logout')
def Signout():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    user = session_username
    auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
    api_url = f'{API_URL}/Signout'
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return render_template('index.html', popup_message = "Logged Out Successfully!")
    return render_template('index.html', popup_message = "Logged Out Successfully!")


@app.route('/userappupdate')
def userappupdate():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    user = session_username
    auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
    
    api_url = f'{API_URL}/ShowSpecificApplications'
    
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 404:
        return render_template('userapplicationupdate.html', popup_message=f'{response.text}')
    data = response.json()
    
    try:
        if data.get('message') == "Session Timeout":
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        pass

    
    return render_template('userapplicationupdate.html', applications=data)

@app.route('/applications')
def fetch_applications():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    user = session_username
    auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
    
    api_url = f'{API_URL}/ShowApplications'
    
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        resp = response.json()
        return render_template('employer-dash.html', popup_message = resp.get('message'))
    else:
        data = response.json()
        
        try:
            if data.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        return render_template('applicationrecieved.html', applications=data)
    
    

@app.route('/appupdate', methods=['GET', 'POST'])
def appupdate():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    user = session_username 
    auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
    
    api_url = f'{API_URL}/ShowApplications'
    
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        applications = response.json()
    else:
        return render_template('index.html', popup_message="Session Expired.")
    
    if request.method == 'POST':
        jobid = request.form['jobid']
        username = request.form['username']
        email = request.form['email']
        process = request.form[f'process_{jobid}']
        title = request.form['title']
        update_url = f'{API_URL}/UpdateApplication'
        request_body = {
            'jobid': jobid,
            'username': username,
            'email': email,
            'process': process,
            'title': title
        }
        
        response = requests.post(update_url, json=request_body, headers=headers)
        output = response.json()
        try:
            if output.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        
        if response.status_code != 200:
            return redirect('updateapplication.html', popup_message = output.get('message'))

        else:
            return render_template('updateapplication.html', popup_message = output.get('message'))

    
    return render_template('updateapplication.html', applications=applications)

@app.route('/apply-job', methods=['POST'])
def apply_job():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    job_id = request.form.get("jobid")
    if not job_id:
        popup_message = "Job Id is required."
        return render_template('userjobs.html', popup_message=popup_message)

    api_url = f"{API_URL}/ApplyApplication"
    user = session_username 
    auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/json"
    }
    payload = {"JobId": job_id}

    try:
        response = requests.post(api_url, headers=headers, json=payload)

        api_response = response.json()
        try:
            if api_response.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass

        return render_template('userjobs.html', popup_message=f'{api_response.get('message')}')
        
    except Exception as ex:
        return render_template('userjobs.html', popup_message=f'Error -> {ex}')

    

@app.route('/userjobs')
def userjobs():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    api_url = f"{API_URL}/ShowJobs"
    
    try:
        
        user = session_username
        
        auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
        response = requests.get(api_url, headers={"Authorization": f"Basic {auth_base64}"})
        api_data = response.json()
        
        try:
            if api_data.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        job_data = []
        for job in api_data: 
            job_entry = {
                "job_id": job[0],
                "created_date": job[1],
                "last_date": job[2],
                "title": job[4],
                "description": job[6],
                "url": job[3],
                "who_can_apply": job[5],
                "required_skills": job[7],
            }
            job_data.append(job_entry)
    except :
        job_data = []

    return render_template('userjobs.html', jobs=job_data)

@app.route('/showjobs')
def showjobs():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    api_url = f"{API_URL}/ShowJobs"
    
    try:
        user = session_username
        auth_base64 = base64.b64encode(user.encode('utf-8')).decode('utf-8')
        response = requests.get(api_url, headers={"Authorization": f"Basic {auth_base64}"})
        api_data = response.json()
        try:
            if api_data.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass

        job_data = []
        for job in api_data: 
            job_entry = {
                "job_id": job[0],
                "created_date": job[1],
                "last_date": job[2],
                "title": job[4],
                "description": job[6],
                "url": job[3],
                "who_can_apply": job[5],
                "required_skills": job[7],
            }
            job_data.append(job_entry)
    except:
        job_data = []

    return render_template('showjobs.html', jobs=job_data)


@app.route('/forgot')
def forgot():
    return render_template('forgot.html', popup_message=None)

    
@app.route('/register')
def register():
    try:
        response_org = requests.get(f'{API_URL}/ListOrganization')
        response_org.raise_for_status()
        org_data = response_org.json()
        org_keys = list(org_data.keys())

    except requests.exceptions.RequestException as e:
        print(f"Organization API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch organizations.", organizations=[])
    try:
        user_types_response = requests.get(f'{API_URL}/ShowUserType')
        user_types_response.raise_for_status()
        user_types = user_types_response.json()
        try:
            if user_types.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
    except requests.exceptions.RequestException as e:
        print(f"User type API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch user types.", organizations=org_keys, usertype=[])

    return render_template('register.html', popup_message=None, organizations=org_keys, usertype=user_types)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        global session_username
        session_username = username

        if not username or not password:
            return render_template('index.html', popup_message="Username and password are required.")

        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_base64}'
        }
        response = requests.post(f'{API_URL}/Login', headers=headers)
        
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get("message") == 'Login successful':
                session_id = f"session_{username}"
                user_sessions[session_id] = {
                    "username": username,
                    "password" : password,
                    "start_time": datetime.now(),
                    "expiry_time": datetime.now() + timedelta(minutes=SESSION_TIMEOUT)
                }
                if api_response.get("UserType") == "Employer":
                    user_data = api_response  
                    return render_template('employer-dash.html', user=user_data)
                else:
                    user_data = api_response 
                    return render_template('user-dash.html', user=user_data)
            else:
                return render_template('index.html', popup_message=api_response.get("message", "Login failed."))
        elif response.status_code == 404:
            return render_template('index.html', popup_message = "User is not registered.")
        elif response.status_code == 401:
            return render_template('index.html', popup_message = "User is not authorized to Access.")
        else:
            return render_template('index.html', popup_message="Credentials are incorrect or User is not registered.")
    except Exception as e:
        return render_template('index.html', popup_message=f"Error: {str(e)}")
    
@app.route('/submit-forgot', methods=['POST'])
def submitforgot():
    try:
        username = request.form.get('username')
        email = request.form.get('email')

        if not username or not email:
            return render_template('forgot.html', popup_message="Username and Email are required.")

        payload = {"username": username, "email": email}
        response = requests.post(f'{API_URL}/ForgotPassword', json=payload)
        messages = response.json()
        try:
            if messages.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        message = messages.get("message")
        return render_template('forgot.html', popup_message=f"{message}")
    except Exception as e:
        return render_template('forgot.html', popup_message=f"Error: {str(e)}")

@app.route('/submit-register', methods=['POST'])
def submitregister():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        skillset = request.form.get('skillset')
        user_type = request.form.get('user_type')
        organization = request.form.get('organization')
        profilepic = request.files.get('profilepic')
        resume = request.files.get('resume')

        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        data = {
            'FirstName': first_name,
            'LastName': last_name,
            'EmailId': email,
            'ContactDetails': contact,
            'SkillSet': skillset,
            'UserType': user_type,
            'Organization': organization
        }

        files = {
            'ProfilePicture': (profilepic.filename, profilepic.stream, profilepic.content_type),
            'Resume': (resume.filename, resume.stream, resume.content_type)
        }

        response = requests.post(f'{API_URL}/Register', headers=headers, data=data, files=files)

        api_response = response.json()
        try:
            if api_response.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        return render_template('register.html', popup_message=f'{api_response.get("message")}')

    except Exception as e:
        return render_template('register.html', popup_message=f"{e}")
    
@app.route('/createjob')
def createjob():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    return render_template('createjob.html')

@app.route('/create_job', methods=['POST'])
def create_job():
    try:
        session_check = CheckSession(session_username, user_sessions)
        if not session_check:
            return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    except:
        return render_template('index.html', popup_message = "Session Timeout! Please Login.")
    title = request.form.get('title')
    description = request.form.get('description')
    skills = request.form.get('skills')
    who_can_apply = request.form.get('who-can-apply')
    apply_url = request.form.get('apply-url')
    last_date = request.form.get('last-date')

    user = session_username  
    encoded_username = base64.b64encode(user.encode('utf-8')).decode('utf-8')  # Base64 encoding

    data = {
        "LastDate": last_date,
        "UrlToApply": apply_url,
        "Title": title,
        "WhoCanApply": who_can_apply,
        "Description": description,
        "RequiredSkillSet": skills
    }

    url = f'{API_URL}/CreateJob'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_username}'
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        return render_template('/create_job', popup_message = response.text)

    try:
        response_data = response.json()
        try:
            if response_data.get('message') == "Session Timeout":
                return render_template('index.html', popup_message = "Session Timeout! Please Login.")
        except:
            pass
        return render_template('/employer-dash.html', popup_message = response_data['message'])
    except:
        return render_template('/employer-dash.html', popup_message = "Unexpected error occured. Contact Admin")
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

