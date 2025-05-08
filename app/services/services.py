from werkzeug.security import generate_password_hash, check_password_hash
from db.connectionToDataBase import DataBaseConnection

class AuthenticationServices():

    @staticmethod
  

    @staticmethod
    def login(userName:str, password):
        conn = DataBaseConnection.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        userName=userName.strip().lower()


        cursor.execute(
            " SELECT * FROM users WHERE username = %s", (userName, ))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            return {"message": "Success", "role":user['role']}
        else:

            return{"message":" Wrong username or password "}
        