import base64
import requests
from flask import Flask, request, render_template

app = Flask(__name__)



API_URL = "http://127.0.0.1:8081/"  # Replace with your actual API URL

@app.route('/')
def index():
    return render_template('index.html', popup_message=None)

@app.route('/forgot')
def forgot():
    return render_template('forgot.html', popup_message=None)

# @app.route('/register')
# def register():
#     try:
#         response_org = requests.get(f'{API_URL}/ListOrganization')
#         if response_org.status_code == 200:
#             org = response_org.json()
#         else:
#             return render_template('register.html', popup_message= "Unable to retrieve Organization List. Please contact Admin.")
#     except:
#         return render_template('register.html', popup_message= "Unable to retrieve Organization List. Please contact Admin.")

#     try:
#         user_types_response = requests.get(f'{API_URL}/ShowUserType')
#         if user_types_response.status_code == 200:
#             user_types = user_types_response.json()
#         else:
#             return render_template('register.html', popup_message= "Unable to retrieve User type List. Please contact Admin.")
#     except:
#         return render_template('register.html', popup_message= "Unable to retrieve User type List. Please contact Admin.")
#     return render_template('register.html', popup_message=None, organiz=org, usertype=user_types)

    
@app.route('/register')
def register():
    try:
        response_org = requests.get(f'{API_URL}/ListOrganization')
        response_org.raise_for_status()
        org = response_org.json()
    except requests.exceptions.RequestException as e:
        print(f"Organization API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch organizations.", organiz={}, usertype=[])

    try:
        user_types_response = requests.get(f'{API_URL}/ShowUserType')
        user_types_response.raise_for_status()
        user_types = user_types_response.json()
    except requests.exceptions.RequestException as e:
        print(f"User type API error: {e}")
        return render_template('register.html', popup_message="Failed to fetch user types.", organiz=org, usertype=[])

    return render_template('register.html', popup_message=None, organiz=org, usertype=user_types)



# @app.route('/register')
# def register():
#     try:
#         response_org = requests.get(f'{API_URL}/ListOrganization')
#         if response_org.status_code == 200:
#             organization = response_org.json()
#         else:
#             organization = {}
#     except:
#         organization = {}

#     try:
#         # Fetch user types from the API
#         user_types_response = requests.get(f'{API_URL}/ShowUserType')
#         if user_types_response.status_code == 200:
#             user_types = user_types_response.json()
#         else:
#             user_types = []  # Default to empty if API fails
#     except Exception as e:
#         user_types = []  # Default to empty if an error occurs

#     return render_template('register.html', popup_message=None, organization=organization, usertype=user_types)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('index.html', popup_message="Username and password are required.")

        # Forward the data to the external API
        payload = {"username": username, "password": password}
        response = requests.post(f'{API_URL}/login', json=payload)
        
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get("message") == 'Login successful':
                return render_template('index.html', popup_message="Login successful!")
            else:
                return render_template('index.html', popup_message=api_response.get("message", "Login failed."))
        elif response.status_code == 404:
            return render_template('index.html', popup_message = "User is not registered.")
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

        response = requests.post(f'{API_URL}/Register', )


        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_base64}'
        }

        # Prepare data to be sent in the POST request as JSON
        data = {
            'FirstName': first_name,
            'LastName': last_name,
            'EmailId': email,
            'ContactDetails': contact,
            'SkillSet': skillset,
            'UserType': user_type,# This might need to be handled differently if it's a file
            'Organization': organization
        }

        files = {
            'ProfilePicture': (profilepic.filename, profilepic.stream, profilepic.content_type),
            'Resume': (resume.filename, resume.stream, resume.content_type)
        }

        # Sending the POST request to the API
        response = requests.post(f'{API_URL}/Register', headers=headers, data=data, files=files)

        
        
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get("message") == 'Registration successful':
                return render_template('register.html', popup_message=f'{response.reason}')
        else:
            return render_template('register.html', popup_message='Error Occured')
    except Exception as e:
        return render_template('register.html', popup_message=f"Error")

if __name__ == '__main__':
    app.run(port=8080, debug=True)
