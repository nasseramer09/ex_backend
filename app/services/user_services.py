from db import connectionToDataBase
from app.models.users_model import User
from werkzeug.security import generate_password_hash

class User_Services:
      
      def get_user_bu_id(self, user_id):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
           return User(*result)
        return None

      
      def createAcount(self, user_data):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        hashed_password= generate_password_hash(user_data['password'])
        
        sql_query = """
            INSERT INTO users (firstname, lastname, username, password_hash, phone_number, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        values = (user_data.get('firstname'),
                user_data.get('lastname'), 
                user_data.get('username'), 
                hashed_password,
                user_data.get('phone_number'),
                user_data.get('role'))
        try:
            cursor.execute(sql_query, values)
            conn.commit()
            user_id= cursor.lastrowid
            cursor.close()
            conn.close()
            return self.get_user_by_id(user_id)
        
        except Exception as e:
           if conn:
              conn.rollback()
           cursor.close()
           conn.close()
           print(f"Fel vid skapandet av användare: {e}")
           return None
      
        