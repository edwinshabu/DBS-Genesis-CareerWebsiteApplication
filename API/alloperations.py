import base64
from datetime import datetime
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
    def CheckSession(username, user_sessions):
        session_id = f"session_{username}"
        if session_id not in user_sessions:
            return None  # No session found
        
        session = user_sessions[session_id]
        if datetime.now() > session["expiry_time"]:
            del user_sessions[session_id]  # Clean up expired session
            return None
        
        # Return the password if the session is valid
        return session.get("password")
  

    def SendEmail(to_email, message):
        smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
        smtp_port = 587
        smtp_user = 'genesiscareer353@gmail.com'  # Replace with your email
        smtp_password = 'vdfi ydtp egfg lrpz'

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = 'Genesis Career'
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
            email_list = [row[0] for row in emails]
            # Return list of emails
            return email_list
        except:
            return "Email Service Error."
        
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

    def ApplyApplication(username, password, job_id):
        try:
            connection = Connection.get_db_connection(username, password)
            if connection.is_connected():
                cursor = connection.cursor()
                user_id = "SELECT Id, Email from Users WHERE Username = %s;"
                cursor.execute(user_id, (username,))
                ids = cursor.fetchone() 
                if ids:
                    id = ids[0]
                    process_step = 'Applied'
                    insert_query = "INSERT INTO Applications (JobId, UserId, ProcessStep) VALUES (%s, %s, %s)"
                    role = "SELECT Title FROM JobPosting WHERE Id = %s;"
                    cursor.execute(role, (job_id,))
                    result = cursor.fetchone()
                    cursor.execute(insert_query, (job_id, id, process_step))
                    connection.commit()
                    title = result[0]
                    message = f"""
Hello {username},

Thanks for applying for the Job Role - {title}. 
You will hear back shortly.

Regards,
Genesis Career
"""
                    AllOperations.SendEmail(id[1], message)
                    return True
                else:
                    id = False
            else:
                return False
        except:
            return False



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
    
    def CheckUserType(username):
        # Establish database connection
        connection = Connection.get_db_connection('root', 'Root@123')
        cursor = connection.cursor()

        try:
            # Query to get the UserTypeId based on the Username
            typeId_query = "SELECT UserTypeId FROM Users WHERE Username = %s;"
            cursor.execute(typeId_query, (username,))
            usertype_id = cursor.fetchone()

            if usertype_id:
                # Query to get the Type based on the UserTypeId
                type_query = "SELECT Type FROM UserType WHERE Id = %s;"
                cursor.execute(type_query, (usertype_id[0],))  # usertype_id[0] contains the Id
                user_type = cursor.fetchone()

                if user_type:
                    return user_type[0]  # Returning the Type
                else:
                    return None  # Type not found for the UserTypeId
            else:
                return None  # User not found

        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()



    def CheckUserTypeId(username):
        # Establish database connection
        connection = Connection.get_db_connection('root', 'Root@123')
        cursor = connection.cursor()

        try:
            # Query to get the UserTypeId based on the Username
            typeId_query = "SELECT Id FROM Users WHERE Username = %s;"
            cursor.execute(typeId_query, (username,))
            user_id = cursor.fetchone()

            if user_id:
                return user_id[0]  # Type not found for the UserTypeId
            else:
                return None  # User not found

        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()





        


class Employer:
    def CheckEmployer(username, password):
        try:
            connection = Connection.get_db_connection(username, password)
            cursor = connection.cursor()
            query = """
    SELECT 
        CASE 
            WHEN ut.Type = 'Employer' THEN TRUE
            ELSE FALSE
        END AS IsEmployer
    FROM Users u
    JOIN UserType ut ON u.UserTypeId = ut.Id
    WHERE u.Username = %s AND u.Password = %s;
    """
            cursor.execute(query, (username, password)) 
            result = cursor.fetchone() 
            return result[0] if result else False
        except Exception as e:
                print(f"Error: {e}")
                return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def CreateJob(data, username, password):
        try:
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
            if non_employer_emails.count != 0 or non_employer_emails == "Email Service Error":
                for email in non_employer_emails:
                    AllOperations.SendEmail(email, message)
            else:
                print("Skipping....................")
            connection.close()

            return jsonify({"message": "Job posting created successfully"}), 201
        except Exception as ex:
            connection.rollback()
            return jsonify({"error": str(ex)}), 500

    def ShowSpecificApplications(username, password):
        try:
                # Establish DB connection
                connection = Connection.get_db_connection(username, password)

                if connection.is_connected():
                    cursor = connection.cursor()
                    id = AllOperations.CheckUserTypeId(username)
                    if type == None:
                        return jsonify({"error": "An unknown error occured. Please contact Admin."}), 500
                    q = "SELECT * FROM Applications WHERE UserId = %s"
                    cursor.execute(q, (id,))
                    rows = cursor.fetchall()
                    if not rows:  # If the list is empty, return an empty JSON array
                        return jsonify({"message": "You have not applied for any Job."}), 200
                    return jsonify(rows), 200

                connection.close()

        except Exception as ex:
            return jsonify({"error": str(ex)}), 500

    def ShowAllApplications(username, password):
        try:
                # Establish DB connection
                connection = Connection.get_db_connection(username, password)

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM Applications;")
                    rows = cursor.fetchall()
                    if not rows:  # If the list is empty, return an empty JSON array
                        return jsonify({"message": "No applications"}), 200
                    return jsonify(rows), 200

                connection.close()

        except Exception as ex:
            return jsonify({"error": str(ex)}), 500
        
    def ShowJobs(username, password):
        try:
                # Establish DB connection
                connection = Connection.get_db_connection(username, password)
                if connection == 500:
                    return jsonify({"message": "Database Connection Service Error. Please contact Administrator."}), 500

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM JobPosting;")
                    rows = cursor.fetchall()
                    if not rows:  # If the list is empty, return an empty JSON array
                        return jsonify({"message": "No Jobs Available right now."}), 200
                    return rows, 200

                connection.close()

        except Exception as ex:
            return jsonify({"error": str(ex)}), 500