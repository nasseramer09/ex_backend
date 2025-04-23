from werkzeug.security import generate_password_hash, check_password_hash
from db.connectionToDataBase import DataBaseConnection

class AuthenticationServices():

    @staticmethod
    def createAcount(firstName:str, lastName:str, userName:str , password:str, role:str):
        conn = DataBaseConnection.get_db_connection()
        cursor = conn.cursor()

        hashed_password= generate_password_hash(password)
        fornamn=firstName.lower()
        efternamn=lastName.lower()
        anvandarnamn=userName.lower()
        rolen = role.strip().lower()
        
        
        print(f"Försöker infoga roll: '{rolen}'")
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, username, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
            """, (fornamn, efternamn, anvandarnamn, hashed_password, rolen)
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("User has being created successfully ")
        

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
        