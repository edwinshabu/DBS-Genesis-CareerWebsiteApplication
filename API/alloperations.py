import base64
import os
from time import sleep
import mysql.connector
from mysql.connector import Error
from database_connector import Connection


from flask import Flask, json, request, jsonify
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AllOperations:
    def SendEmail(to_email, message):
        smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
        smtp_port = 587
        smtp_user = 'genesiscareer353@gmail.com'  # Replace with your email
        smtp_password = 'vdfi ydtp egfg lrpz'

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = 'Genesis Career - User Password.'
        body = f'{message}'
        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def GetAllEmail():
        try:
            connection = Connection.get_db_connection('root', 'Root@123')
            cursor = connection.cursor()
            cursor.execute("""
        SELECT Email FROM Users 
        WHERE UserTypeId != (SELECT Id FROM UserType WHERE Type = 'Employer')
    """)
            emails = cursor.fetchall()

            if len(emails) == 0:
                return "Email Service Error",404
            connection.close()
    
            # Return list of emails
            return [email[0] for email in emails],200
        except:
            return "Email Service Error.",500

    def ShowOrganizations():
        try:
            connection = Connection.get_db_connection('root', 'Root@123')
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT o.Name, ot.Type
                FROM Organization o
                JOIN OrganizationType ot ON o.OrganizationTypeId = ot.Id;
                """
                cursor.execute(query)
                result = cursor.fetchall()
                org_dict = {}
                for row in result:
                    org_dict[row['Name']] = row['Type']
                org_json = json.dumps(org_dict, indent=4)
                cursor.close()
                connection.close()

                return org_json,200
            
        except Exception as ex:
            return jsonify({"message": f"{ex}"}), 500 

    def ShowUserTypes():
        try:
            connection = Connection.get_db_connection('root', 'Root@123')
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = "SELECT Type from UserType;"
                cursor.execute(query)
                result = cursor.fetchall()
                
                # Extract only the 'Type' values into a list
                types = [row['Type'] for row in result]
                
                cursor.close()
                connection.close()

                return types, 200
                
        except Exception as ex:
            return jsonify({"message": f"Unable to establish connection to Database. Please contact Administrator."}), 500

        

    def ListAllUsers():
        try:
            # Establish the connection
            connection = Connection.get_db_connection('root', 'Root@123')

            if connection.is_connected():
                # Create a cursor to execute the query
                cursor = connection.cursor()

                # Query to retrieve unique usernames from the `mysql.user` table
                query = "SELECT DISTINCT User FROM mysql.user;"
                cursor.execute(query)

                # Fetch all usernames
                usernames = [row[0] for row in cursor.fetchall()]

                # Close the cursor and connection
                cursor.close()
                connection.close()

                return usernames

        except Error as e:
            print(f"Error: {e}")
            return []
    
    def DeleteUser(username):
        try:
            # Establish the connection to the application database
            connection = Connection.get_db_connection('root', 'Root@123')

            if connection.is_connected():
                cursor = connection.cursor()

                # Drop the user from the MariaDB server
                cursor.execute("DROP USER IF EXISTS %s;", (username,))
                connection.commit()

                # Create a cursor to execute the query

                # Query to check if the user exists in the application database (Users table)
                cursor.execute("SELECT Id FROM Users WHERE Username = %s;", (username,))
                user_data = cursor.fetchone()

                if user_data:
                    user_id = user_data[0]

                    # Delete dependent entries from JobPosting table
                    cursor.execute("DELETE FROM JobPosting WHERE UserId = %s;", (user_id,))
                    
                    # Delete dependent entries from Applications table
                    cursor.execute("DELETE FROM Applications WHERE UserId = %s;", (user_id,))

                    # Now delete the user from the Users table
                    cursor.execute("DELETE FROM Users WHERE Id = %s;", (user_id,))
                    connection.commit()

                    cursor.close()
                    connection.close()

                    # Establish a connection to the MariaDB server for dropping the user

            else:
                return f"Connection to Database Failed! Due to some reason."

            return f"User '{username}' and associated records deleted successfully from both the application database and the MariaDB server."

        except Error as e:
            print(f"Error: {e}")
            return f"Error occurred: {e}"


class Employer:
    def CreateJob(data):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith("Basic "):
                # Extract base64 part of the header
                base64_credentials = auth_header.split(" ")[1]
                # Decode the base64 string
                decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")
                # Split into username and password
                username, password = decoded_credentials.split(":", 1)
            else:
                return jsonify({"message": "User is not registered with us."}), 404
                
            last_date = data.get("LastDate")
            url = data.get("UrlToApply")
            title = data.get("Title")
            whocan = data.get("WhoCanApply")
            description = data.get("Description")
            required_skill_set = data.get("RequiredSkillSet")

            message = f"""
    Dear User,

    We are excited to announce a new job posting:

    Title: {title}
    Posted On: {last_date}
    URL: {url}
    
    Description:
    {description}
    
    Who can apply: {whocan}
    
    Required Skill Set:
    {required_skill_set}
    
    Thank you,
    Genesis Career Team
    """
            connection = Connection.get_db_connection(username, password)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT Id FROM Users WHERE Username = %s;", (username,))
                user_id_data = cursor.fetchone()
                if user_id_data:
                    user_id = user_id_data[0]
                    cursor.execute("""
            INSERT INTO JobPosting (LastDate, UrlToApply, Title, WhoCanApply, Description, RequiredSkillSet, UserId)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (last_date, url, title, whocan, description, required_skill_set, user_id))
                    connection.commit()
                else:
                    connection.rollback()
                    return jsonify({"message": "User is not properly registered."}), 404
           
            non_employer_emails = AllOperations.GetAllEmail()
            if non_employer_emails[1] == 500:
                connection.rollback()
                return  jsonify({"message": "Email Service Error."}), 500
            elif non_employer_emails[1] == 404:
                connection.rollback()
                print("Skipping.............. Email as there is no users.")
            elif non_employer_emails[1] == 200:
                for email in non_employer_emails:
                    if non_employer_emails == 200:
                        break
                    AllOperations.SendEmail(email[0], message)
            connection.close()

            return jsonify({"message": "Job posting created successfully"}), 201
        except Exception as ex:
            connection.rollback()
            return jsonify({"error": str(ex)}), 500

    
    def ShowApplications():
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith("Basic "):
                # Extract base64 part of the header
                base64_credentials = auth_header.split(" ")[1]
                # Decode the base64 string
                decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")
                # Split into username and password
                username, password = decoded_credentials.split(":", 1)

                # Establish DB connection
                connection = Connection.get_db_connection(username, password)

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM Applications;")
                    rows = cursor.fetchall()
                    if not rows:  # If the list is empty, return an empty JSON array
                        return jsonify({"message": "No applications"}), 200
                    return jsonify(rows)

                connection.close()

        except Exception as ex:
            return jsonify({"error": str(ex)}), 500
        
    def ShowJobs():
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith("Basic "):
                # Extract base64 part of the header
                base64_credentials = auth_header.split(" ")[1]
                # Decode the base64 string
                decoded_credentials = base64.b64decode(base64_credentials).decode("utf-8")
                # Split into username and password
                username, password = decoded_credentials.split(":", 1)

                # Establish DB connection
                connection = Connection.get_db_connection(username, password)

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM JobPosting;")
                    rows = cursor.fetchall()
                    if not rows:  # If the list is empty, return an empty JSON array
                        return jsonify({"message": "No Jobs Available right now."}), 200
                    return jsonify(rows)

                connection.close()

        except Exception as ex:
            return jsonify({"error": str(ex)}), 500