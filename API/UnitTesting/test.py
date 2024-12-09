import unittest
from unittest.mock import patch
from app import app

class TestRegisterAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    @classmethod
    @patch('app.Operations.Register')
    def test_register_success(cls, mock_register):
        # Mock the return value of Operations.Register
        mock_register.return_value = "Registration successful"

        # Simulate a POST request to the /Register endpoint
        response = cls.app.post('/Register', data={
            'username': 'testuser',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'contact': '1234567890',
            'skillset': 'Python, Flask',
            'user_type': 'Developer',
            'organization': 'TestOrg'
        }, content_type='multipart/form-data',
        files={
            'profilepic': ("profile.jpg", b"fake_image_data", "image/jpeg"),
            'resume': ("resume.pdf", b"fake_pdf_data", "application/pdf")
        })

        # Assert the mock was called with the correct data
        mock_register.assert_called_with({
            'username': 'testuser',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'contact': '1234567890',
            'skillset': 'Python, Flask',
            'user_type': 'Developer',
            'organization': 'TestOrg'
        })

        # Assert the response status code and data (JSON)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Registration successful"  # Assuming 'message' is the key

    @classmethod
    @patch('app.Operations.Register')
    def test_register_failure(cls, mock_register):
        # Mock the return value of Operations.Register
        mock_register.return_value = "Registration failed"

        # Simulate a POST request to the /Register endpoint
        response = cls.app.post('/Register', data={
            'username': '',  # Missing username
            'password': 'password123',
            'first_name': '',
            'last_name': '',
            'email': 'testuser@example.com',
            'contact': '1234567890',
            'skillset': 'Python, Flask',
            'user_type': 'Developer',
            'organization': 'TestOrg'
        }, content_type='multipart/form-data',
        files={
            'profilepic': ("profile.jpg", b"fake_image_data", "image/jpeg"),
            'resume': ("resume.pdf", b"fake_pdf_data", "application/pdf")
        })

        # Assert the mock was called with the correct data
        mock_register.assert_called_with({
            'username': '',
            'password': 'password123',
            'first_name': '',
            'last_name': '',
            'email': 'testuser@example.com',
            'contact': '1234567890',
            'skillset': 'Python, Flask',
            'user_type': 'Developer',
            'organization': 'TestOrg'
        })

        # Assert the response status code and data (JSON)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Registration failed"  # Assuming 'message' is the key

if __name__ == '__main__':
    unittest.main()
