from flask import Flask, request, jsonify
import re
from mysql.connector import Error
from database_connector import Connection, DBOperations
from alloperations import AllOperations
import base64
import mysql.connector

class Validation:
    def validate_email(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_contact(contact):
        contact_regex = r'^[0-9]{10}$'  # Assuming 10 digit contact numbers
        return re.match(contact_regex, contact) is not None

    def validate_password(password):
        # Must have at least one uppercase, one lowercase, one number, and be at least 8 characters long
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        return re.match(password_regex, password) is not None

class Operations:

    def Login(data):
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        connection = Connection.get_db_connection(username,password)
        if connection == 500:
            return jsonify({'message': 'Either User is not registered or Credentials are incorrect.'}), 500
        # return jsonify({'message': 'Login Success'}), 200
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Query to check if the username and password exist in the user table
            query = "SELECT * FROM Users WHERE Username = %s"
            cursor.execute(query, (username,))
            
            result = cursor.fetchone()
            if result:
                # Convert binary data to Base64 string for ProfilePic and Resume if they exist
                if result.get('ProfilePic'):
                    result['ProfilePic'] = base64.b64encode(result['ProfilePic']).decode('utf-8')
                if result.get('Resume'):
                    result['Resume'] = base64.b64encode(result['Resume']).decode('utf-8')
                cursor.close()
                connection.close() 
                return jsonify({'message': 'Login successful', 'user': result}), 200
            else:
                cursor.close()
                connection.close() 
                return jsonify({'message': 'User is not registered.'}), 404
        except Error as e:
            cursor.close()
            connection.close() 
            return jsonify({'message': f"Error: {e}"}), 500

    def Check_User(username):
        try:
            conn = Connection.get_db_connection('root', 'Root@123')
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM mysql.user WHERE user = '{username}';")
            result = cursor.fetchone()
            return result[0] > 0  # Returns True if user exists
        except Error as e:
            print(f"Error checking user existence: {e}")
            return False

    
    def Create_NewUser(username, password):
        try:
            if Operations.Check_User(username):
                return {"message": f"User '{username}' already exists."}, 409
            conn = Connection.get_db_connection('root', 'Root@123')
            cursor = conn.cursor()
            cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}';")
        
            # Grant CRUD permissions
            cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {'GenesisCareer'}.* TO '{username}'@'%';")
            
            # Apply changes
            cursor.execute("FLUSH PRIVILEGES;")
            conn.commit()
            
            
            return {"message": f"User '{username}' created successfully with CRUD permissions."}, 201
        
        except Error as e:
            return {"error": str(e)}, 400
        


    def Register(data):
        first_name = data.get('FirstName')
        last_name = data.get('LastName')
        email = data.get('EmailId')
        username = data.get('Username')
        password = data.get('Password')
        contact = data.get('ContactDetails')
        user_type = data.get('UserType')
        skill_set = data.get('SkillSet')
        org = data.get('Organization')
        
        # Extracting files (profile picture and resume)
        profile_picture = request.files.get('ProfilePicture')
        resume = request.files.get('Resume')

        result, status_code = Operations.Create_NewUser(username, password)
    
        if status_code == 409:  # User already exists
            return {"status": "exists", "message": result["message"]}
        if status_code != 201:  # Error occurred
            return {"status": "error", "message": result.get("error", "Unknown error")}
        
        # Validation
        if not Validation.validate_email(email):
            return jsonify({"message": "Invalid email format"}), 400
        if not Validation.validate_contact(contact):
            return jsonify({"message": "Invalid contact number"}), 400
        if not Validation.validate_password(password):
            return jsonify({"message": "Invalid Password"}), 400


        # Get the UserTypeId from UserType table
        user_type_id = DBOperations.GetUserType(username, password, user_type)
        if not user_type_id:
            return jsonify({"message": "Invalid UserType"}), 400

        # Convert profile picture and resume to binary (BLOB)
        profile_picture_blob = None
        if profile_picture:
            profile_picture_blob = profile_picture.read()

        resume_blob = None
        if resume:
            resume_blob = resume.read()
        
        # Establish database connection
        conn = Connection.get_db_connection(username, password)
        cursor = conn.cursor()

        try:

            cursor.execute(f"SELECT Id FROM Organization WHERE Name = '{org}';")
            org_id_data = cursor.fetchone()
            org_id = org_id_data[0]
            # Insert user data into Users table
            cursor.execute(""" 
                INSERT INTO Users (FirstName, LastName, Email, Username, Password, Contact, ProfilePic, Resume, Skills, UserTypeId, OrganizationId)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, username, password, contact, profile_picture_blob, resume_blob, skill_set, user_type_id, org_id))

            conn.commit()
            return jsonify({"message": "Registration successful"}), 201
        except mysql.connector.Error as err:
            conn.rollback()
            return jsonify({"message": f"Database error: {err}"}), 500
        finally:
            cursor.close()
            conn.close()

    def ForgotPassword(username, emailId):
        try:
            connection = Connection.get_db_connection('root', 'Root@123')
            cursor = connection.cursor()
            query = "SELECT password FROM Users WHERE username = %s AND email = %s"
            cursor.execute(query, (username, emailId))
            result = cursor.fetchone()
            if result == None:
                return jsonify({"message" : "User is not registered."}), 404
            if result:
                password = result[0]
                message = f"""
    Hello {username},

    This is your password for the Genesis Career Login.

    Password: '{password}'

    Regards,
    """
                if  AllOperations.SendEmail(emailId, message):
                    return jsonify({"message": "Password sent to email successfully"}), 200

            
        except Exception as ex:
            return jsonify({"error": f"An error occurred: {str(ex)}"}), 500
