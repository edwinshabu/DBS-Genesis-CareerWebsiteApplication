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

if __name__ == '__main__':
    app.run(port=8080, debug=True)
