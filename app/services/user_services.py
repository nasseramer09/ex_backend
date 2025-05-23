import mysql.connector
from ..db import connectionToDataBase
from app.models.users_model import User
from werkzeug.security import generate_password_hash, check_password_hash

class User_Services:
      
      def get_user_by_id(self, user_id):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
               return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            sql_query = """
                           SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email, is_occupied
                              FROM users WHERE id = %s
                              """
                        
            cursor.execute(sql_query, (user_id,))
            result = cursor.fetchone()
            
            if result:
               return User(*result), 200
            return {"message": f"Kunde inte hitta användare med id: {user_id}"}, 404 
        
        except Exception as e:
            print(f"Fel vid hämtning av användare med id {user_id}: {e}")
            return {"message": f"Kunde inte hämta användare med id: {user_id} på grund av ett fel: {e}"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

      def get_all_users(self):
        conn = None
        cursor = None
        try:
           
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
               return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            sql_query = """
            SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email, is_occupied FROM users
            """
            cursor.execute(sql_query)
            result = cursor.fetchall()

            users = []
            for row in result:
               users.append(User(*row))
            return users, 200
        except Exception as e:
            print(f"Fel vid hämtning av alla användare: {e}")
            return {"message": f"Kunde inte hämta användare på grund av ett fel: {e}"}, 500
      
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
      
      def createAccount(self, user_data):
        conn=None
        cursor=None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
               
                return {"message": "Kunde inte ansluta till databasen"}, 500
            cursor = conn.cursor()

            password = user_data.get('password')

            if not password:
               return {"message": "Lösenord saknas."}, 400

            hashed_password= generate_password_hash(password)
            
            sql_query = """
                  INSERT INTO users (first_name, last_name, username, password_hash, role, phone_number, email, is_occupied )
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                  """
            values = (user_data.get('first_name'),
                     user_data.get('last_name'), 
                     user_data.get('username'), 
                     hashed_password,
                     user_data.get('role'),
                     user_data.get('phone_number'),
                     user_data.get('email'),
                     False 
                     )
                     
            cursor.execute(sql_query, values)
            conn.commit()
            user_id= cursor.lastrowid

            new_user, status_kod = self.get_user_by_id(user_id)
            return new_user, status_kod
   

        except mysql.connector.Error as e:
           if conn:
              conn.rollback()
           print(f"Fel vid skapandet av användare (database fel): {e}")

           if "Duplicate entery " in str(e) and "username" in str(e):
               return {"message": "Användarnamnet finns redan "}, 409
           
           elif "Duplicate entery " in str(e) and "email" in str(e):
               return {"message": "E-postadressen finns redan {e}"}, 409
           
           else:
              return {"message": "Något blev fel vid skapandet av användaren: {e}"}, 500
        except Exception as e:
            if conn:
               conn.rollback()
            print(f"Något gick fel vid skapandet av användaren: {e}")
            return {"message": "Något blev fel vid skapandet av användaren."}, 500
        finally:
           if cursor:
              cursor.close()
           if conn:
              conn.close()
         


      def update_user(self, user_id, user_data):
            conn = None
            cursor = None
            try:

               conn = connectionToDataBase.DataBaseConnection.get_db_connection()
               if not conn:
                  return {"message": "Kunde inte ansluta till databasen"}, 500

               cursor = conn.cursor()

               updated_fields = []
               values = []

               for key, value in user_data.items():
                  if key == 'password':
                     hashed_password = generate_password_hash(value)
                     updated_fields.append("password_hash = %s")
                     values.append(hashed_password)

                  elif key in ['first_name', 'last_name', 'username', 'role', 'phone_number', 'email', 'is_occupied']:
                     updated_fields.append(f"{key} = %s")
                     values.append(value)


               if not updated_fields:
                 
                  return self.get_user_by_id(user_id), 200
               

               if 'username' in user_data:
                  existing_user = self.get_user_by_email(user_data['email'])

                  if existing_user and existing_user.id != user_id:
                     return {"message": "Användarnamnet eller E-postadressen används redan av en annan användare."}, 409

               
               sql_query = f"UPDATE users SET {', '.join(updated_fields)} WHERE id = %s"
               values.append(user_id)

               cursor.execute(sql_query, tuple(values))
               conn.commit()

               if cursor.rowcount == 0:
                  return {"message": f"Kunde inte hitta användare med ID {user_id} att uppdatera."}, 404

               return self.get_user_by_id(user_id)

            except mysql.connector.Error as e:
               if conn:
                  conn.rollback()   
               
               print(f"Fel vid uppdatering av användaren (database fel): {e}")
               return {"message": f"Fel vid uppdatering av användaren med id {user_id}: {e}"}, 500
            
            except Exception as e:
               
                  if conn:
                     conn.rollback()
                  print(f"Något gick fel vid uppdatering av användaren: {e}")
                  return {"message": "Något blev fel vid uppdatering av användaren."}, 500
            finally:
               if cursor:
                  cursor.close()

               if conn:
                  conn.close()

   
      def delete_user(self, user_id):
         conn = None
         cursor = None

         try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
               return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()

            #kolla om användaren är aktiv i något uppdrag innan borttagningen
            cursor.execute(""" SELECT COUNT(*) FROM task_users tu JOIN tasks t ON tu.task_id = t.id WHERE tu.user_id = %s AND t.status IN ('planerat', 'pågående')
               """, (user_id,))
            
            active_tasks_count = cursor.fetchone()[0]

            if active_tasks_count > 0:
               return {"message": f"Kunde inte ta bort användare med id {user_id}. Den är kopplad till {active_tasks_count} pågående eller planerade uppdrag."}, 409 # Conflict
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            conn.commit()

            if cursor.rowcount > 0:
               return {"message": f"Användare med id {user_id} har tagits bort"}, 200
            
            else:
               return {"message": f"Kunde inte hitta användare med id {user_id} för att ta bort"}, 404
         
         except mysql.connector.Error as e:
            if conn:
               conn.rollback()
            
            print(f"Fel vid borttagandet av användaren (database fel): {e}")
            return {"message": f"Något blev fel vid borttagandet av användaren med id {user_id}: {e}"}, 500
         
         except Exception as e:
            if conn:
               conn.rollback()

            print(f"Något gick fel vid borttagandet av användaren: {e}")
            return {"message": "Något blev fel vid borttagandet av användaren."}, 500
         
         finally:
            if cursor:
               cursor.close()
            if conn:
               conn.close()
      
      def get_user_by_email(self, email):
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
               return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            sql_query="""
                           SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_at, email, is_occupied 
                              FROM users WHERE email = %s
                              """
            cursor.execute(sql_query, (email,))
            result = cursor.fetchone()

            if result:
               return User(*result), 200
            return {"message": f"Kunde inte hitta användare med e-post: {email}"}, 404
        except Exception as e:
             print(f"Fel vid hämtning av användare med e-post {email}: {e}")
             return {"message": f"Kunde inte hämta användare med e-post: {email} på grund av ett fel: {e}"}, 500
        
        finally: 
            if cursor:
                cursor.close()
            if conn:
                conn.close()


      def verify_password(self, user, password):
         if user and check_password_hash(user.password_hash, password):
            return True
         return False