import unittest
import base64
import json
from urllib import request

from flask import Flask
import requests
from app import app
import random
import string


app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem
session = requests.Session()
user_sessions = {}
SESSION_TIMEOUT = 3000

def generate_random_email(domain="gmail.com"):
    # Generate a random username with lowercase letters and digits
    username_length = random.randint(5, 10)  # Username length between 5 and 10 characters
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    
    # Combine the username with the domain
    email = f"{username}@{domain}"
    return email

class TestRegisterAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    def test_Register_Check_If_User_Exist(self):
        # Prepare the username and password for authorization
        username = "andtrds"
        password = "Admin@123456"
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Simulate a POST request to the /Register endpoint
        with open('resume.pdf', 'rb') as resume, open('pic.jpg', 'rb') as pic:
            response = self.app.post(
                '/Register',
                data={
                    'FirstName': 'Tester',
                    'LastName': 'User',
                    'EmailId': 'ted8dsdtusdds@exadmple.com',
                    'ContactDetails': '7742477777',
                    'SkillSet': 'Python, Flask',
                    'UserType': 'Employee',
                    'Organization': 'TechCorp',
                    'Resume': resume,
                    'ProfilePicture': pic
                },
                content_type='multipart/form-data',
                headers=headers
            )

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the response status code
        self.assertEqual(response_data.get('message'), 'User exists!')

    def test_Register_Check_Missing_Fields(self):
        length = 8
        characters = string.ascii_lowercase + string.digits
        random_username = ''.join(random.choice(characters) for _ in range(length))
        random_number = random.randint(1000000000, 9999999999)

        # Prepare the username and password for authorization
        username = random_username
        password = "Admin@123456"
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Simulate a POST request to the /Register endpoint
        with open('resume.pdf', 'rb') as resume, open('pic.jpg', 'rb') as pic:
            response = self.app.post(
                '/Register',
                data={
                    'FirstName': 'Tester',
                    'LastName': 'User',
                    'EmailId': '',  # Missing EmailId
                    'ContactDetails': f'{random_number}',
                    'SkillSet': 'Python, Flask',
                    'UserType': 'Employee',
                    'Organization': 'TechCorp',
                    'Resume': resume,
                    'ProfilePicture': pic
                },
                content_type='multipart/form-data',
                headers=headers
            )

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the response status code
        self.assertEqual(response.status_code, 400)  # Bad Request for missing field
        self.assertEqual(response_data.get('message'), 'EmailId is required')
    
    def test_Register_Successful(self):
        length = 8
        characters = string.ascii_lowercase + string.digits
        random_username = ''.join(random.choice(characters) for _ in range(length))
        random_number = random.randint(1000000000, 9999999999)
        random_email = generate_random_email()

        # Prepare the username and password for authorization
        username = random_username
        password = "Admin@123456"
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Simulate a POST request to the /Register endpoint
        with open('resume.pdf', 'rb') as resume, open('pic.jpg', 'rb') as pic:
            response = self.app.post(
                '/Register',
                data={
                    'FirstName': 'Tester',
                    'LastName': 'User',
                    'EmailId': f'{random_email}',  
                    'ContactDetails': f'{random_number}',
                    'SkillSet': 'Python, Flask',
                    'UserType': 'Employee',
                    'Organization': 'TechCorp',
                    'Resume': resume,
                    'ProfilePicture': pic
                },
                content_type='multipart/form-data',
                headers=headers
            )

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the response status code
        self.assertEqual(response_data.get('message'), 'Registration successful')
    
    def test_Register_AlreadyExist(self):
        random_number = random.randint(1000000000, 9999999999)
        random_email = generate_random_email()

        # Prepare the username and password for authorization
        username = 'pete'
        password = "Admin@123456"
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Simulate a POST request to the /Register endpoint
        with open('resume.pdf', 'rb') as resume, open('pic.jpg', 'rb') as pic:
            response = self.app.post(
                '/Register',
                data={
                    'FirstName': 'Tester',
                    'LastName': 'User',
                    'EmailId': f'{random_email}',  
                    'ContactDetails': f'{random_number}',
                    'SkillSet': 'Python, Flask',
                    'UserType': 'Employee',
                    'Organization': 'TechCorp',
                    'Resume': resume,
                    'ProfilePicture': pic
                },
                content_type='multipart/form-data',
                headers=headers
            )

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the response status code
        self.assertEqual(response_data.get('message'), 'User exists!')
    

    def test_Register_Check_Contact_Validation(self):
        length = 8
        characters = string.ascii_lowercase + string.digits
        random_username = ''.join(random.choice(characters) for _ in range(length))
        random_number = random.randint(0, 99999)
        random_email = generate_random_email()

        # Prepare the username and password for authorization
        username = random_username
        password = "Admin@123456"
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        # Prepare headers with the Base64 encoded Authorization
        headers = {
            'Authorization': f'Basic {auth_base64}',
        }

        # Simulate a POST request to the /Register endpoint
        with open('resume.pdf', 'rb') as resume, open('pic.jpg', 'rb') as pic:
            response = self.app.post(
                '/Register',
                data={
                    'FirstName': 'Tester',
                    'LastName': 'User',
                    'EmailId': f'{random_email}',  
                    'ContactDetails': f'{random_number}',
                    'SkillSet': 'Python, Flask',
                    'UserType': 'Employee',
                    'Organization': 'TechCorp',
                    'Resume': resume,
                    'ProfilePicture': pic
                },
                content_type='multipart/form-data',
                headers=headers
            )

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the response status code
        self.assertEqual(response_data.get('message'), 'Invalid contact number')

    def test_Login_Check_Not_Registered(self):
            username = 'admin'
            password = 'Admin@123'  # Missing password field
            
            auth_string = f"{username}:{password}"
            auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            # Prepare headers with the Base64 encoded Authorization
            headers = {
                'Authorization': f'Basic {auth_base64}',
            }
            
            # Simulate a POST request to the /Login endpoint
            response = self.app.post(
                '/Login',
                headers=headers
            )

            # Parse the JSON response
            response_data = json.loads(response.data.decode())
            print(response_data)

            # Assert the response status code and error message
            self.assertEqual(response_data.get('message'), "User is not registered!")

    def test_Login_Check_Not_Registered(self):
            username = 'admin'
            password = 'Admin@123'  # Missing password field
            
            auth_string = f"{username}:{password}"
            auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            # Prepare headers with the Base64 encoded Authorization
            
            # Simulate a POST request to the /Login endpoint
            response = self.app.post(
                '/Login'
            )

            # Parse the JSON response
            response_data = json.loads(response.data.decode())
            print(response_data)

            # Assert the response status code and error message
            self.assertEqual(response_data.get('message'), "Authentication header is missing.")
        
    
if __name__ == '__main__':
    unittest.main()

