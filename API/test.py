import base64
from io import BytesIO
import os
import unittest
from app import app   # assuming the Flask app is in 'app.py'
from flask import json
from werkzeug.datastructures import FileStorage

API_URL = 'http://127.0.0.1:8081'

class TestRegistration(unittest.TestCase):
    def setUp(self):
        # Create a test client for the Flask app
        self.client = app.test_client()
        # Set up any necessary configuration here
        self.app = app

    def test_register_success(self):
        # Sample data for registration
        username = 'tester'
        password = 'Password@123'
        auth_string = f"{username}:{password}"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/json'
        }
        form_data = {
            'FirstName': 'Tester',
            'LastName': 'Testing',
            'EmailId': '20040425@mydbs.ie',
            'ContactDetails': '9730343371',
            'SkillSet': 'Python,JavaScript,SQL',
            'UserType': 'Employer',
            'Organization': 'TechCorp'
        }
        
        # Create FileStorage objects for files
        profilepic_file = BytesIO(b"fake_image_data")
        profilepic = FileStorage(profilepic_file, filename='pic.jpg', content_type='image/jpeg')

        resume_file = BytesIO(b"fake_pdf_data")
        resume = FileStorage(resume_file, filename='resume.pdf', content_type='application/pdf')

        # Files dictionary
        files = {
            'ProfilePicture': profilepic,
            'Resume': resume
        }

        # Simulate a POST request to the /Register endpoint with form data and files
        data = form_data
        data['ProfilePicture'] = profilepic
        data['Resume'] = resume

        # Send request with multipart/form-data content type
        response = self.client.post(f'{API_URL}/Register', 
                                    data=data,
                                    headers=headers)

        # Assert the response status code and message
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertIn('message', response_json)  # Assumes the success message is in the response
        self.assertEqual(response_json['message'], 'User registered successfully')  # Replace with actual message

if __name__ == '__main__':
    unittest.main()
