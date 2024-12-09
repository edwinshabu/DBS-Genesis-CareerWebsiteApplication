from flask import jsonify
import mysql.connector
from mysql.connector import Error

class Connection:
    #  def get_db_connection(username, password):
    #     try:
    #         # Attempting to connect to the database with the provided credentials
    #         connection = mysql.connector.connect(
    #             host='localhost',  # Your MariaDB host
    #             database='genesiscareer',  # Your database name
    #             user=username,  # Your MariaDB username
    #             password=password  # Your MariaDB password
    #         )

    #         if connection.is_connected():
    #             # Check if the user exists in the database
    #             cursor = connection.cursor()
    #             cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    #             user_count = cursor.fetchone()[0]

    #             if user_count == 0:
    #                 return 404

    #             # If the user exists, you can now verify the password
    #             cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    #             stored_password = cursor.fetchone()[0]

    #             if stored_password != password:
    #                 return None, "Incorrect password."

    #             return connection, None  # Successful login, no error message

    #     except Exception as e:
    #         # Catch all other exceptions (e.g., unexpected issues)
    #         print(f"Unexpected error: {e}")
    #         return None, f"Unexpected error: {str(e)}"
        
    #     return None, "Unknown error occurred."

    def get_db_connection(username, password):
        try:
            connection = mysql.connector.connect(
                host='localhost',  # Your MariaDB host
                database='genesiscareer',  # Your database name
                user= username,  # Your MariaDB username
                password= password  # Your MariaDB password
            )
            if connection.is_connected():
                return connection, 200
        except Error as e:
            return "Error occured while creating connection to Database. Contact Administrator.", 500
        

class DBOperations:    
    def GetUserType(username, password, user_type):
        try:
            # Connect to the database and fetch the UserTypeId based on user_type
            conn, status = Connection.get_db_connection(username, password)
            if status != 200:
                return conn, status
            cursor = conn.cursor()
            cursor.execute("SELECT Id FROM UserType WHERE Type = %s", (user_type,))
            user_type_id = cursor.fetchone()
            conn.close()
            if user_type_id:
                return user_type_id[0], 200
            else:
                return "UserType not found. Contact Admin", 500
        except Exception as ex:
            print(ex)
            return "Unable to retrieve USerType from database. Contact Administrator.", 500

