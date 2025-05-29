import mysql.connector
from ..db import connectionToDataBase
from app.models.users_model import User
from app.models.tasks_model import Task
from werkzeug.security import generate_password_hash, check_password_hash

class User_Services:
    def _get_user_with_relations(self, user_id):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor(dictionary=True)

            sql_user_query = """
                SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email, is_occupied
                FROM users WHERE id = %s
            """
            cursor.execute(sql_user_query, (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                return {"message": f"Kunde inte hitta användare med id: {user_id}"}, 404

            sql_tasks_query = """
                SELECT t.id, t.title, t.description, t.start_time, t.end_time,
                       t.start_adress, t.destination_adress, t.status
                FROM tasks t
                JOIN task_users tu ON t.id = tu.task_id
                WHERE tu.user_id = %s
            """
            cursor.execute(sql_tasks_query, (user_id,))
            assigned_tasks_raw = cursor.fetchall()
            assigned_tasks_details = []

            for task_row in assigned_tasks_raw:
                
                assigned_tasks_details.append({
                    'id': task_row['id'],
                    'title': task_row['title'],
                    'description': task_row['description'],
                    'start_time': task_row['start_time'].isoformat() if task_row['start_time'] else None,
                    'end_time': task_row['end_time'].isoformat() if task_row['end_time'] else None,
                    'start_adress': task_row['start_adress'],
                    'destination_adress': task_row['destination_adress'],
                    'status': task_row['status']
                })

            user_obj = User(
                id=user_data['id'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                username=user_data['username'],
                role=user_data['role'],
                password_hash=user_data['password_hash'],
                phone_number=user_data['phone_number'],
                created_at=user_data['created_At'],
                email=user_data['email'],
                is_occupied=user_data['is_occupied'],
                assigned_tasks=assigned_tasks_details
            )
            return user_obj, 200

        except Exception as e:
            print(f"Fel vid hämtning av användare med relationer för id {user_id}: {e}")
            return {"message": f"Kunde inte hämta användare med id: {user_id} på grund av ett fel: {e}"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_user_by_id(self, user_id):
        return self._get_user_with_relations(user_id)

    def get_all_users(self):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                print("Database connection failed")
                return None, 500

            cursor = conn.cursor()
            sql_query = """
            SELECT id, first_name, last_name, username, role, password_hash, phone_number, created_At, email, is_occupied
            FROM users
            """
            cursor.execute(sql_query)
            result = cursor.fetchall()

            if not result:
                return [], 200

            users = []
            for row in result:
                try:
                    users.append(User(*row))
                except Exception as e:
                    print(f"Error creating User object from row: {e}")
                    continue

            if not users:
                return {"message": "Inga användare hittades"}, 404
            return users, 200

        except mysql.connector.Error as e:
            print(f"Database error when fetching users: {e}")
            return {"message": "Databasfel vid hämtning av användare"}, 500
        except Exception as e:
            print(f"Unexpected error when fetching users: {e}")
            return {"message": "Ett oväntat fel uppstod vid hämtning av användare"}, 500
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
         

    def update_user_internal(self, user_id, user_data, existing_cursor=None):
            conn = None
            local_cursor = None
            try:
               if existing_cursor is None:
                  conn = connectionToDataBase.DataBaseConnection.get_db_connection()
                  local_cursor=conn.cursor()
                  cursor_to_use = local_cursor
               else:
                  cursor_to_use = existing_cursor

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

                  curent_user, status_kod = self.get_user_by_id(user_id)
                  if status_kod ==200:
                     return curent_user, 200
                  else:
                     return {"message": "Inga giltiga fält att uppdatera"}, 400

               if 'username' in user_data:
                  check_user_sql="SELECT id FROM users WHERE username = %s AND id !=%s"
                  cursor_to_use.execute(check_user_sql, (user_data['username'], user_id))
                  if cursor_to_use.fetchone():
                     return {"message": "Användarnamnet används redan av en annan användare."}, 409

               if 'email' in user_data:
                  check_email_sql="SELECT id FROM users WHERE email = %s AND id !=%s"
                  cursor_to_use.execute(check_email_sql, (user_data['email'], user_id))
                  if cursor_to_use.fetchone():
                     return {"message": " E-postadressen används redan av en annan användare."}, 409
               
               sql_query = f"UPDATE users SET {', '.join(updated_fields)} WHERE id = %s"
               values.append(user_id)

               cursor_to_use.execute(sql_query, tuple(values))

               if existing_cursor is None:
                  conn.commit()
                  updated_user, status = self.get_user_by_id(user_id)
                  if status == 200:
                     return updated_user, 200
                  else:
                      return {"message": f"Kunde inte hämta uppdaterad användare med ID {user_id}."}, 500
               else:
                     return {"message": "Användare uppdaterad internt"}, 200

            except mysql.connector.Error as e:
               if conn and existing_cursor is None:
                  conn.rollback()
               print(f"Fel vid uppdatering av användaren (database fel): {e}")
               return {"message": f"Fel vid uppdatering av användaren"}, 500
            
            except Exception as e:
                  if conn and existing_cursor is None:
                     conn.rollback()
                  print(f"Något gick fel vid uppdatering av användaren: {e}")
                  return {"message": "Något blev fel vid uppdatering av användaren."}, 500
            finally:
               if local_cursor:
                  local_cursor.close()

               if conn:
                  conn.close()

    def update_user(self, user_id, user_data):
         return self.update_user_internal(user_id, user_data, existing_cursor=None)
   
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