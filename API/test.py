from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database Admin Credentials
DB_HOST = "localhost"  # Change to your database host
DB_ADMIN_USER = "root"  # Admin username
DB_ADMIN_PASSWORD = "Root@123"  # Admin password
TARGET_DATABASE = "GenesisCareer"  # Change to your database name


def user_existss(admin_connection, username):
    """Check if a user already exists in the database."""
    try:
        cursor = admin_connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM mysql.user WHERE user = '{username}';")
        result = cursor.fetchone()
        return result[0] > 0  # Returns True if user exists
    except Error as e:
        print(f"Error checking user existence: {e}")
        return False


def create_new_user(admin_connection, username, password):
    """Create a new user and grant CRUD permissions."""
    try:
        # Check if the user already exists
        if user_existss(admin_connection, username):
            return {"message": f"User '{username}' already exists."}, 409

        cursor = admin_connection.cursor()
        # Create new user
        cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}';")
        
        # Grant CRUD permissions
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {TARGET_DATABASE}.* TO '{username}'@'%';")
        
        # Apply changes
        cursor.execute("FLUSH PRIVILEGES;")
        admin_connection.commit()
        
        return {"message": f"User '{username}' created successfully with CRUD permissions."}, 201
    except Error as e:
        return {"error": str(e)}, 400


@app.route('/test', methods=['POST'])
def create_user():
    """API Endpoint to create a new database user."""
    try:
        # Parse JSON input
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {"error": "Username and password are required."}, 400

        # Connect to the database as admin
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_ADMIN_USER,
            password=DB_ADMIN_PASSWORD
        )
        
        if connection.is_connected():
            # Create the new user
            response, status_code = create_new_user(connection, username, password)
            connection.close()
            return response, status_code
        else:
            return {"error": "Failed to connect to the database as admin."}, 500

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
