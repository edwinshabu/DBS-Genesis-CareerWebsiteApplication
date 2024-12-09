from flask import jsonify
import mysql.connector
from mysql.connector import Error

class Connection:
    def get_db_connection(username, password):
        try:
            connection = mysql.connector.connect(
                host='localhost', 
                database='genesiscareer',  
                user= username,  
                password= password
            )
            if connection.is_connected():
                return connection, 200
        except Error as e:
            return "Error occured while creating connection to Database. Contact Administrator.", 500
        

class DBOperations:    
    def GetUserType(username, password, user_type):
        try:
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

