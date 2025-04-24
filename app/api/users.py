from flask import Falsk, jsonify, request
import app
from db import connectionToDataBase
from werkzeug.security import generate_password_hash

@app.route('/create_user', methods=['POST'])
def createAcount(firstName:str, lastName:str, userName:str , password:str, role:str):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
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
        return{"message": "User has being created successfully "}
        