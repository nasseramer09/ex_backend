from ..db import connectionToDataBase
from app.models.users_model import User
from werkzeug.security import generate_password_hash, check_password_hash

class User_Services:
      
      def get_user_by_id(self, user_id):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email" 
                        " FROM users WHERE id = %s", (user_id,)
                     )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
           return User(*result)
        return None
      

      def get_all_users(self):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email" 
                        " FROM users "
                     )
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        users = []
        for row in result:
           users.append(User(*row))
        return users

      
      def createAccount(self, user_data):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()

        if not conn:
           
           return None, 500
        cursor = conn.cursor()
        hashed_password= generate_password_hash(user_data['password_hash'])
        
        sql_query = """
            INSERT INTO users (first_name, last_name, username, password_hash, role, phone_number, email )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        values = (user_data.get('first_name'),
                user_data.get('last_name'), 
                user_data.get('username'), 
                hashed_password,
                user_data.get('role'),
                user_data.get('phone_number'),
                user_data.get('email'))
               
                
        try:
            cursor.execute(sql_query, values)
            conn.commit()
            user_id= cursor.lastrowid
            cursor.close()
            conn.close()
            return self.get_user_by_id(user_id), 201
        
        except Exception as e:
           if conn:
              conn.rollback()
           cursor.close()
           conn.close()
           print(f"Fel vid skapandet av användare: {e}")
           if "Duplicate entery" in str(e):
              return {"message": f"Användarnamnet finns redan "}, 400
           else:
              return {"message": f"Något blev fel {e}"}, 500
      
        
      def update_user(self, user_id, user_data):
         conn = connectionToDataBase.DataBaseConnection.get_db_connection()
         cursor = conn.cursor()
         updated_fields = []
         values = []

         for key, value in user_data.items():
            if key == 'password':
               hashed_password = generate_password_hash(value)
               updated_fields.append(f"{key}_hash = %s")
               values.append(hashed_password)

            elif key not in ['id', 'created_at']:
               updated_fields.append(f"{key} = %s")
               values.append(value)

         if not updated_fields:
            cursor.close()
            conn.close()
            return self.get_user_by_id(user_id) # ingen data/fält är uppdaterad?
           
         sql_query = f"UPDATE users SET {', '.join(updated_fields)} WHERE id = %s"
         values.append(user_id)

         try:
            cursor.execute(sql_query, tuple(values))
            conn.commit()
            cursor.close()
            conn.close()
            return self.get_user_by_id(user_id)
         except Exception as e:
            if conn:
               conn.rollback()
            cursor.close()
            conn.close()
            print(f"Fel vid uppdatering av användaren: {e}")
            return None
   
      def delete_user(self, user_id):
         conn = connectionToDataBase.DataBaseConnection.get_db_connection()
         cursor = conn.cursor()

         try:
            cursor.execute(" DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0 # Detta kommer att kolla om annat rad kommer att påverkad av bortagningen
         except Exception as e:
            if conn:
               conn.rollback()
               print(f"Fel vid bortagandet av användaren: {e}")
               return False
         finally:
            cursor.close()
            conn.close()
      
      def get_user_by_email(self, email):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email" 
                        " FROM users WHERE email = %s", (email,)
                     )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
           return User(*result)
        return None
      
      def verify_password(self, user, password):
         if user and check_password_hash(user.password_hash, password):
            return True
         return False