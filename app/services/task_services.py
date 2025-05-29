import datetime
import mysql.connector
from app.services.car_services import Car_services
from app.services.user_services import User_Services
from app.models.users_model import User
from app.models.car_model import Car
from ..db import connectionToDataBase
from app.models.tasks_model import Task

class Task_services:
    def __init__(self):
        self.car_services = Car_services()
        self.user_services = User_Services()


    def create_task(self, task_data):
        conn=None
        cursor=None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()

            title = task_data.get('title')
            description = task_data.get('description')
            start_time_str = task_data.get('start_time')
            end_time_str = task_data.get('end_time')
            car_ids = task_data.get('car_ids', [])
            assigned_users = task_data.get('assigned_users', [])
            start_adress = task_data.get('start_adress')
            destination_adress = task_data.get('destination_adress')
            status = task_data.get('status', 'planerat')

            if not all([title, start_time_str, end_time_str, start_adress, destination_adress]):
                return {"message": "Alla nödvändiga fält (title, start_time, end_time, start_adress, destination_adress) måste fyllas i."}, 400

            try:
                start_time = datetime.datetime.fromisoformat(start_time_str)
                end_time = datetime.datetime.fromisoformat(end_time_str)
            except ValueError:
                return {"message": "Ogiltigt format för start_time eller end_time. Använd ISO-format (YYYY-MM-DDTHH:MM:SS)."}, 400

            if end_time<= start_time:
                return {"message": "Sluttiden måste vara efter starttiden."}, 400
            
            #chekcs if car is free
            for car_id in car_ids:
                car, car_status_kod = self.car_services.get_car_by_id(car_id)

                if car_status_kod != 200:
                    return {"message": f"Fordon med ID {car_id} hittades inte."}, 404
                
                if car.is_occupied:
                    return {"message": f"Fordon med ID {car_id} är redan upptaget."}, 409 # Conflict

            #checks if user is free
            for user_id in assigned_users:
                user, user_status_kod = self.user_services.get_user_by_id(user_id)

                if user_status_kod !=200:
                    return {"message": f"Användare med ID {user_id} hittades inte."}, 404

                if user.is_occupied:
                    return {"message": f"Användare med ID {user_id} är redan upptagen."}, 409 # Conflict

            sql_query_task="""
                        INSERT INTO tasks (title, description, start_time, end_time, start_adress, destination_adress, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
            values_task = ( title, description, start_time, end_time, start_adress, destination_adress, status)
            
            cursor.execute(sql_query_task, values_task)
            conn.commit()

            task_id = cursor.lastrowid

            if not task_id:
                return {"message": "Kunde inte hämta uppgift"}, 500

            #connects car to task if any cars are assigned
            if car_ids:
                for car_id in car_ids:
                    sql_query_task_car = "INSERT INTO task_cars (task_id, car_id) VALUES (%s, %s)"
                    cursor.execute(sql_query_task_car, (task_id, car_id ))

                    update_car_result, uppdate_car_status = self.car_services.update_car_internal(car_id, {'is_occupied': True, 'status':'upptagen'}, cursor)

                    if uppdate_car_status !=200:
                        print(f"Varning: Kunde inte uppdatera bil {car_id} status under task creation: {update_car_result}")

            #connect user to task if any users are assigned
            if assigned_users:
                for user_id in assigned_users:
                    sql_query_task_user = "INSERT INTO task_users (task_id, user_id) VALUES (%s, %s)"
                    cursor.execute(sql_query_task_user, (task_id, user_id))

                    update_user_result, uppdate_user_status = self.user_services.update_user_internal(user_id, {'is_occupied': True}, cursor)

                    if uppdate_user_status !=200:
                        print(f"Varning: Kunde inte uppdatera användare {user_id} status under task creation: {update_user_result}")

            conn.commit()
            return self._get_task_with_relations(task_id)
        
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
                print(f"Fel vid skapandet av uppgift (databasfel): {e}")
                return {"message": f"Något blev fel vid skapandet av uppgiften: {e}"}, 500
       
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Något gick fel vid skapandet av tasken: {e}")
                return {"message": "Något blev fel vid skapandet av tasken."}, 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return {"message": "Ett oväntat fel uppstod vid skapandet av uppgiften."}, 500


    def _get_task_with_relations(self, task_id):
        
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                            SELECT id, title, description, start_time, end_time, start_adress, destination_adress, status
                           FROM tasks WHERE id = %s
                           """, (task_id,))
            
            task_results = cursor.fetchone()

            if not task_results:
                return {"message": f"Kunde inte hitta uppgifter med id: {task_id}"}, 404
            
            cursor.execute("SELECT car_id FROM task_cars WHERE task_id = %s", (task_id,))
            car_ids= [row['car_id'] for row in cursor.fetchall()]
            car_details = []

            if car_ids:
                placeholder =', '.join(['%s'] * len(car_ids))
                sql_cars_query=f"SELECT id, model, license_plate, status, is_occupied FROM cars WHERE id IN ({placeholder})"
                

                cursor.execute(sql_cars_query, tuple(car_ids))

                for car_row in cursor.fetchall():
                    car_details.append({
                        'id': car_row['id'],
                        'model': car_row['model'],
                        'license_plate': car_row['license_plate'],
                        'status':car_row['status'],
                        'is_occupied':car_row['is_occupied']
                        
                    })

            cursor.execute("SELECT user_id FROM task_users WHERE task_id = %s", (task_id,))
            assigned_users_ids = [row['user_id'] for row in cursor.fetchall()]

            assigned_users_details = []
            if assigned_users_ids:
                placeholder =', '.join(['%s'] * len( assigned_users_ids))
                sql_users_query=f"SELECT id, username, first_name, last_name, email FROM users WHERE id IN ({placeholder})"

                cursor.execute(sql_users_query, tuple(assigned_users_ids))

                for user_row in cursor.fetchall():
                    assigned_users_details.append({
                        'id':user_row['id'],
                        'username':user_row['username'],
                        'first_name':user_row['first_name'],
                        'last_name':user_row['last_name'],
                        'email':user_row['email']
                    })

            task_obj = Task(
                id=task_results['id'],
                title=task_results['title'],
                description=task_results['description'],
                start_time=task_results['start_time'],
                end_time=task_results['end_time'],
                start_adress=task_results['start_adress'],
                destination_adress=task_results['destination_adress'],
                status=task_results['status'],
                car_ids=car_ids,
                assigned_users=assigned_users_ids
            )
            response_data = task_obj.to_dic()
            response_data['assigned_users_details'] = assigned_users_details
            response_data['car_details'] = car_details
            return response_data, 200
        
        except Exception as e:
            print(f"Fel vid hämtning av uppgift med relationer: {e}")
            return {"message": f"Fel vid hämtning av uppgift med id {task_id}: {e}"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

    def get_task_by_id(self, task_id):
        return self._get_task_with_relations(task_id)
    
    def get_all_tasks(self):
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            sql_query=("""
                       SELECT id, title, description, start_time, end_time, start_adress, destination_adress, status
                        FROM tasks ORDER BY id DESC
                       """)

            cursor.execute(sql_query)
            all_tasks_data = cursor.fetchall()

            tasks_list = []
            for task_data in all_tasks_data:
                task_id= task_data[0]
                task_detail_reposnse, status_code = self._get_task_with_relations(task_id)

                if status_code == 200:
                    tasks_list.append(task_detail_reposnse)
                else:
                    print(f" Kunde inte hämta fullständig data för task ID {task_id}: {task_detail_reposnse['message']}")
            return tasks_list, 200
        
        except Exception as e:
            print(f"Fel vid hämtning av all uppgifter : {e}")
            return {"message": f"Kunde inte hämta uppgifter {e}:"}, 500
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def update_task(self, task_id, task_data):
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            

            cursor = conn.cursor()
            updated_fields = []
            values = []
            allowed_status_status=['planerat', 'pågående', 'avbrutet', 'klart']

            car_ids_to_update = task_data.get('car_ids')
            assigned_users_to_update  = task_data.get('assigned_users')


            curent_task,curent_task_status_kod = self._get_task_with_relations(task_id)
            if curent_task_status_kod !=200:
                return curent_task, curent_task_status_kod 
            
            old_car_ids = curent_task.get('car_ids', [])
            old_assigned_users = curent_task.get('assigned_users', [])


            for key, value in task_data.items():
                if key == 'status' and value not in allowed_status_status:
                    return {"message": f"Ogiltig status {value}. Tillåtna värden är {allowed_status_status}"}, 400
                elif key in ['title', 'description', 'start_adress', 'destination_adress', 'status']:
                    updated_fields.append(f"{key} = %s")
                    values.append(value)
                elif key == 'start_time':
                    try:
                        start_time = datetime.datetime.fromisoformat(value)
                        updated_fields.append("start_time = %s")
                        values.append(start_time)
                    except ValueError:
                        return {"message": "Ogiltigt format för start_time. Använd ISO-format."}, 400
                elif key == 'end_time':
                    try:
                        end_time = datetime.datetime.fromisoformat(value)
                        updated_fields.append("end_time = %s")
                        values.append(end_time)
                    except ValueError:
                        return {"message": "Ogiltigt format för end_time. Använd ISO-format."}, 400
            
          
                if not updated_fields and car_ids_to_update is None and assigned_users_to_update is None:
                    return curent_task, 200
                

                if updated_fields:

                    sql_query_task= f"UPDATE tasks SET {', '.join(updated_fields)} WHERE id = %s"
                    values.append(task_id)
                   
                    cursor.execute(sql_query_task, tuple(values))
                
                if car_ids_to_update is not None:
                    free_cars = set(old_car_ids) - set(car_ids_to_update)

                    for car_id in free_cars:
                        cursor.execute("SELECT COUNT(*) FROM task_cars WHERE car_id = %s AND task_id !=%s", (car_id, task_id))

                        if cursor.fetchone()[0] == 0:
                            self.car_services.update_car_internal(car_id, {'is_occupied': False, 'status':'ledig'})

                    car_to_free = set(car_ids_to_update) - set(old_car_ids)
                    for car_id in car_to_free:
                        car, car_status= self.car_services.get_car_by_id(car_id)
                        if car_status !=200 or not isinstance(car, dict) and not isinstance(car, Car):
                            raise ValueError(f"Fordon med ID {car_id} hittades inte för tilldelning.")
                        
                        
                        self.car_services.update_car_internal(car_id, {'is_occupied': True})
                        cursor.execute("INSERT INTO task_cars (task_id, car_id) VALUES (%s, %s)", (task_id, car_id))


                    cars_to_remove= set(old_car_ids) - set(car_ids_to_update)
                    for car_id in cars_to_remove:
                        cursor.execute("DELETE FROM task_cars WHERE task_id = %s AND car_id = %s", (task_id, car_id))

                if assigned_users_to_update is not None:
                    user_to_free = set(old_assigned_users) - set(assigned_users_to_update)

                    for user_id in user_to_free:
                        cursor.execute(" SELECT COUNT(*) FROM task_users WHERE user_id = %s AND task_id != %s", (user_id, task_id))

                        if cursor.fetchone()[0] == 0:
                            self.user_services.update_user_internal(user_id, {'is_occupied': False,  'status':'ledig'})
                    

                    user_to_assgin = set(assigned_users_to_update) - set(old_assigned_users)
                    for user_id in user_to_assgin:
                        user, user_status_kod = self.user_services.get_user_by_id(user_id)

                        if user_status_kod !=200 or not isinstance(user, User):
                            raise ValueError(f"Användare med ID {user_id} hittades inte för tilldelning.")
                        self.user_services.update_user_internal(user_id, {'is_occupied': True})
                        cursor.execute("INSERT INTO task_users (task_id, user_id) VALUES (%s,%s)", (task_id, user_id))
                    
                    
                    users_to_remove = set(old_assigned_users) - set(assigned_users_to_update)
                    for user_id in users_to_remove:
                        cursor.execute("DELETE FROM task_users WHERE task_id =%s AND user_id = %s", (task_id, user_id))

                conn.commit()
                return self._get_task_with_relations(task_id)
            
        except mysql.connector.Error as e:
                if conn:
                    conn.rollback()

                print(f"Fel vid uppdatering av task (database fel): {e}")
                return {"message": f"Fel vid uppdatering av uppgiften med id {task_id}: {e}"}, 500
        
        except ValueError as e:
            if conn:
                conn.rollback()
            print(f"Valideringsfel vid uppdatering av task: {e}")
            return {"message": str(e)}, 400
        
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Något gick fel vid uppdatering av tasken: {e}")
            return {"message": "Något blev fel vid uppdatering av uppgiften."}, 500
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


                
    def delete_task(self, task_id):
        conn = None
        cursor=None

        try:
            conn=connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            
            cursor= conn.cursor()

            task_to_delete, status_code = self._get_task_with_relations(task_id)

            if status_code != 200:
                return {"message": f"Kunde inte hitta uppgift med id {task_id} för att ta bort"}, 404

            cursor.execute(" DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()

            if cursor.rowcount > 0:
                for car_id in task_to_delete.get('car_ids', []):
                    cursor.execute("""
                                    SELECT COUNT(*) FROM task_cars tc JOIN tasks t on tc.task_id = t.id
                                   WHERE tc.car_id = %s AND t.status IN ('planerat', 'pågående') AND tc.task_id != %s """, 
                                   (car_id, task_id))
                    
                    if cursor.fetchone()[0] == 0:
                        self.car_services.update_car_internal(car_id, {'is_occupied': False, 'status':'ledig'}, cursor)

                for user_id in task_to_delete.assigned_users:
                    cursor.execute("""
                                    SELECT COUNT(*) FROM task_users tu JOIN tasks t on tu.task_id = t.id
                                   WHERE tu.user_id = %s AND t.status IN ('planerat', 'pågående') AND tu.task_id != %s """,
                                    (user_id, task_id))
                    
                    
                    if cursor.fetchone()[0] == 0:
                        self.user_services.update_user_internal(user_id, {'is_occupied': False}, cursor)

                return {"message": f" uppgift med id {task_id} har tagits bort"}, 204
                    
            else:
                        return {"message": f" Kunde inte hitta uppgift med id {task_id} för at ta bort"}, 404

        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            print(f"Fel vid borttagandet av tasken (database fel): {e}")
            return {"message": f"Något blev fel vid borttagandet av uppgiften med id {task_id}: {e}"}, 500
    
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Något gick fel (database fel) {e}")
                return {"message": "Något blev fel vi borttagandet av uppgiften med id {task_id}: {e} "}, 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_user_tasks(self, user_id):
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()

            sql_query = """
                SELECT t.id 
                FROM tasks t
                JOIN task_users tu ON t.id = tu.task_id
                WHERE tu.user_id = %s
                ORDER BY t.start_time DESC
            """
            
            cursor.execute(sql_query, (user_id,))
            task_ids = [row[0] for row in cursor.fetchall()]

            tasks_list = []
            for task_id in task_ids:
                task_detail_response, status_code = self._get_task_with_relations(task_id)
                if status_code == 200:
                    tasks_list.append(task_detail_response)
                else:
                    print(f"Kunde inte hämta fullständig data för task ID {task_id}: {task_detail_response['message']}")
            
            return tasks_list, 200
        
        except Exception as e:
            print(f"Fel vid hämtning av användarens uppgifter: {e}")
            return {"message": f"Kunde inte hämta användarens uppgifter: {e}"}, 500
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()