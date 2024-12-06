import base64
import requests
from flask import Flask, redirect, request, render_template, url_for

app = Flask(__name__)



API_URL = "http://127.0.0.1:8081/"  # Replace with your actual API URL

@app.route('/')
def index():
    return render_template('index.html', popup_message=None)

@app.route('/employer-dash')
def empdash():
    return render_template('employer-dash.html', popup_message=None)

@app.route('/applications')
def fetch_applications():
    # Replace 'your-username' and 'your-password' with actual credentials
    username = 'pete'
    auth_base64 = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    
    # API endpoint
    api_url = f'{API_URL}/ShowApplications'
    
    # Make a GET request to the API with the Authorization header
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
    else:
        data = []
    
    # Render the HTML page and pass data to the template
    return render_template('applicationrecieved.html', applications=data)

# @app.route('/appupdate')
# def appupdate():
#     username = 'pete'
#     auth_base64 = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    
#     # API endpoint
#     api_url = f'{API_URL}/ShowApplications'
    
#     # Make a GET request to the API with the Authorization header
#     headers = {
#         'Authorization': f'Basic {auth_base64}'
#     }
    
#     response = requests.get(api_url, headers=headers)
    
#     if response.status_code == 200:
#         data = response.json()
#     else:
#         data = []
    
#     # Render the HTML page and pass data to the template
#     return render_template('updateapplication.html', applications=data)

# @app.route('/appupdate', methods=['GET', 'POST'])
# def appupdate():
#     username = 'pete'  # This should be dynamically set based on the logged-in user
#     auth_base64 = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    
#     # API endpoint for getting applications
#     api_url = f'{API_URL}/ShowApplications'
    
#     # Make a GET request to the API with the Authorization header
#     headers = {
#         'Authorization': f'Basic {auth_base64}'
#     }
    
#     response = requests.get(api_url, headers=headers)
    
#     if response.status_code == 200:
#         applications = response.json()
#     else:
#         return render_template('index.html', popup_message="Session Expired.")
    
#     # Handle the POST request to update application status
#     if request.method == 'POST':
#         # Retrieve the jobid, username, and status from the form
#         jobid = request.form['jobid']
#         username = request.form['username']
#         email = request.form['email']  # Get the email from the hidden input field
#         process = request.form[f'process_{jobid}'] 
#         # Construct the request body for updating the application status
#         update_url = f'{API_URL}/UpdateApplication'
#         request_body = {
#             'jobid': jobid,
#             'username': username,
#             'email': email,  # Add email to the request body
#             'process': process 
#         }
        
#         # Send the POST request to update the application
#         response = requests.post(update_url, json=request_body, headers=headers)
        
#         if response.status_code == 200:
#             message = response.json().get('message', 'Unknown error')
#             if message == "Application Updated!":
#                 return render_template('updateapplication.html', popup_message="Application updated!")

#             else:
#                 return render_template('updateapplication.html', popup_message="Failed to update the Application.")

#         else:
#             return render_template('updateapplication.html', popup_message="Failed to update the Application.")
    
#     # Render the HTML page and pass data to the template
#     return render_template('updateapplication.html', applications=applications)

@app.route('/appupdate', methods=['GET', 'POST'])
def appupdate():
    username = 'pete'  # This should be dynamically set based on the logged-in user
    auth_base64 = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    
    # API endpoint for getting applications
    api_url = f'{API_URL}/ShowApplications'
    
    # Make a GET request to the API with the Authorization header
    headers = {
        'Authorization': f'Basic {auth_base64}'
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        applications = response.json()
    else:
        return render_template('index.html', popup_message="Session Expired.")
    
    # Handle the POST request to update application status
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
        
        if response.status_code == 200:
            message = response.json().get('message', 'Unknown error')
            if message == "Application Updated!":
                return redirect(url_for('appupdate'))  # Redirect after successful update
            else:
                return render_template('updateapplication.html', popup_message="Failed to update the Application.")
        else:
            return render_template('updateapplication.html', popup_message="Failed to update the Application.")
    
    # Render the HTML page with the latest applications data
    return render_template('updateapplication.html', applications=applications)

@app.route('/showjobs')
def showjobs():
    # Replace with the actual API endpoint
    api_url = f"{API_URL}/ShowJobs"
    
    try:
        username = 'pete'
        # Make a GET request to fetch data from the API
        auth_base64 = base64.b64encode(username.encode('utf-8')).decode('utf-8')
        response = requests.get(api_url, headers={"Authorization": f"Basic {auth_base64}"})
        response.raise_for_status()  # Raise an exception for HTTP errors
        api_data = response.json()

        # Process and prepare job data for rendering
        job_data = [
            {
                "created_date": job[1],
                "last_date": job[2],
                "title": job[4],
                "description": job[6],
                "url": job[3],
                "who_can_apply": job[5],
                "required_skills": job[7],
            }
            for index, job in enumerate(api_data) if index != 0 and index != len(api_data) - 1
        ]
    except requests.RequestException as e:
        # Log error and provide fallback data or error message
        print(f"Error fetching data from API: {e}")
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
        org_data = response_org.json()  # Get the JSON response
        org_keys = list(org_data.keys())  # Extract only the keys

    except requests.exceptions.RequestException as e:
        print(f"Organization API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch organizations.", organizations=[])
    try:
        user_types_response = requests.get(f'{API_URL}/ShowUserType')
        user_types_response.raise_for_status()
        user_types = user_types_response.json()
    except requests.exceptions.RequestException as e:
        print(f"User type API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch user types.", organizations=org_keys, usertype=[])

    return render_template('register.html', popup_message=None, organizations=org_keys, usertype=user_types)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('index.html', popup_message="Username and password are required.")

        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_base64}'
        }
        # Forward the data to the external API
        response = requests.post(f'{API_URL}/Login', headers=headers)
        
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get("message") == 'Login successful':
                if api_response.get("UserType") == "Employer":
                    user_data = api_response  # Store user data (if needed) in session or a context variable
                    return render_template('employer-dash.html', user=user_data)
                else:
                    return render_template('index.html', popup_message="You are not authorized to access the employer dashboard.")
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

        # Forward the data to the external API
        payload = {"username": username, "email": email}
        response = requests.post(f'{API_URL}/ForgotPassword', json=payload)
        
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get("message") == 'Password sent to your registered Email.':
                return render_template('forgot.html', popup_message="Password sent to your registered Email.")
            else:
                return render_template('forgot.html', popup_message=api_response.get("message", "Unable to send verify the Identity. Please contact the Admin."))
        elif response.status_code == 404:
            return render_template('forgot.html', popup_message = "Either the Username or the Email Address is not registered.")
        else:
            return render_template('forgot.html', popup_message="Unexpected error occured. Please contact the Admin.")
    except Exception as e:
        return render_template('forgot.html', popup_message=f"Error: {str(e)}")

@app.route('/submit-register', methods=['POST'])
def submitregister():
    try:
        # Get data from the form
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

        # Encode the credentials for Basic Auth
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Prepare the data to send in the POST request (use form data)
        data = {
            'FirstName': first_name,
            'LastName': last_name,
            'EmailId': email,
            'ContactDetails': contact,
            'SkillSet': skillset,
            'UserType': user_type,
            'Organization': organization
        }

        # Prepare the files to be sent in the POST request
        files = {
            'ProfilePicture': (profilepic.filename, profilepic.stream, profilepic.content_type),
            'Resume': (resume.filename, resume.stream, resume.content_type)
        }

        # Sending the POST request to the API
        response = requests.post(f'{API_URL}/Register', headers=headers, data=data, files=files)

        # Check the response status
        if response.status_code == 201:  # Successful registration
            api_response = response.json()
            if api_response.get("message") == 'Registration successful':
                return render_template('register.html', popup_message='Registration successful')
        else:
            # Handle other error responses
            api_response = response.json() if response.content else {}
            error_message = api_response.get("message", "An error occurred during registration.")
            return render_template('register.html', popup_message=f'Error: {error_message}')
    
    except Exception as e:
        # Handle any exceptions that occur
        print(f"Exception: {e}")
        return render_template('register.html', popup_message="An unexpected error occurred.")
    
@app.route('/createjob')
def createjob():
    return render_template('createjob.html')

@app.route('/create_job', methods=['POST'])
def create_job():
    title = request.form.get('title')
    description = request.form.get('description')
    skills = request.form.get('skills')
    who_can_apply = request.form.get('who-can-apply')
    apply_url = request.form.get('apply-url')
    last_date = request.form.get('last-date')

    username = 'pete'  # Replace with actual username
    encoded_username = base64.b64encode(username.encode('utf-8')).decode('utf-8')  # Base64 encoding

    # Prepare the request body
    data = {
        "LastDate": last_date,
        "UrlToApply": apply_url,
        "Title": title,
        "WhoCanApply": who_can_apply,
        "Description": description,
        "RequiredSkillSet": skills
    }

    # Make the API request
    url = f'{API_URL}/CreateJob'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_username}'
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        response_data = response.json()
        if 'message' in response_data:
            # Success message
            return render_template('employer-dash.html', popup_message="Job posting created successfully.")
    elif 'timeout' in response_data:
            return render_template('index.html', popup_message="Session Timeout. Please Login.")
    else:
        # Handle failure
        return render_template('index.html', popup_message="Unknow error occured. Please contact Administrator.")



if __name__ == '__main__':
    app.run(port=8080, debug=True)
