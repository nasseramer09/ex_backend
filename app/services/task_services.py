import datetime
import mysql.connector
from app.services.car_services import Car_services
from app.services.user_services import User_Services
from app.models.users_model import User
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
                return None, 500

            cursor = conn.cursor()

            title = task_data.get('title')
            description = task_data.get('description')
            start_time_str = task_data.get('start_time')
            end_time_str = task_data.get('end_time')
            car_ids = task_data.get('car_ids', [])
            assigned_users=task_data.get('assigned_users', [])
            start_adress = task_data.get('start_adress')
            destination_adress = task_data.get('destination_adress')
            status = task_data.get('status', 'planerat')

            if not all([title, start_time_str, end_time_str, start_adress, destination_adress]):

                return {"message": "Alla nödvändiga fält (title, start_time, end_time, start_adress, destination_adress) måste fyllas i."}, 400
            
            if not car_ids:
                   return {"message": "Minst ett fordon måste tilldelas uppgiften."}, 400
            
            if not assigned_users:
                return {"message": "Minst en användare måste tilldelas uppgiften."}, 400

            try:
                start_time = datetime.datetime.fromisoformat(start_time_str)
                end_time = datetime.datetime.fromisoformat(end_time_str)
            except ValueError:
                return {"message": "Ogiltigt format för start_time eller end_time. Använd ISO-format (YYYY-MM-DDTHH:MM:SS)."}, 400

            if end_time<= start_time:
                return {"message": "Sluttiden måste vara efter starttiden."}, 400
            
            estimated_time = int((end_time - start_time).total_seconds() / 60)

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
                        INSERT INTO tasks (title, description, start_time, end_time, estimated_time, start_adress, destination_adress, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
            values_task = ( title, description, start_time, end_time, estimated_time, start_adress, destination_adress, status)
            
            cursor.execute(sql_query_task, values_task)
            conn.commit()
            task_id=cursor.lastrowid

            #connects car to task
            for car_id in car_ids:
                sql_query_task_car = "INSERT INTO task_cars (task_id, car_id) VALUES (%s, %s)"
                cursor.execute(sql_query_task_car, (task_id, car_id ))

                update_car_result, uppdate_car_status = self.car_services.update_car(car_id, {'is_occupied': True, 'status':'upptagen'})

                if uppdate_car_status !=200:
                    print(f"Varning: Kunde inte uppdatera bil {car_id} status under task creation: {update_car_result}")

            #connect user to task
            for user_id in assigned_users:
                sql_query_task_user = "INSERT INTO task_users (task_id, user_id) VALUES (%s, %s)"
                cursor.execute(sql_query_task_user, (task_id, user_id))

                update_user_result, uppdate_user_status = self.user_services.update_user(user_id, {'is_occupied': True})

                if uppdate_user_status !=200:
                    print(f"Varning: Kunde inte uppdatera bil {car_id} status under task creation: {update_user_result}")

            conn.commit()
            return self._get_task_with_relations(task_id)
        
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
                print(f"Fel vid skapandet av uppgift (databasfel): {e}")

            if "Duplicate entry" in str(e):
                return {"message": "En uppgift med liknande data finns redan."}, 400
            else:
                return {"message": f"Något blev fel vid skapandet av uppgiften: {e}"}, 500
       
        except Exception as e:
            if conn:
                conn.rollback()
                print(f" Fel vid skapandet av task (database fel): {e}")
            if "Dupplicate entry" in str(e):
                return {"message": f"En task med liknande data finns redan."}, 400
            else:
                return {"message": f"Något blev fel vid skapandet av tasken: {e}"}, 500

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


    def _get_task_with_relations(self, task_id):
        
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            
            cursor = conn.cursor()

            #gets tasks
            cursor.execute("""
                            SELECT id, title, description, start_time, end_time, estimated_time, start_adress, destination_adress, status
                           FROM tasks WHERE id = %s
                           """, (task_id,))
            
            task_results = cursor.fetchone()

            if not task_results:
                return {"message": f"Kunde inte hitta uppgifter med id: {task_id}"}, 404

            #gets cars connected to task 
            cursor.execute("SELECT car_id FROM task_cars WHERE task_id = %s", (task_id,))
            car_ids= [row[0] for row in cursor.fetchall()]

            #gets users connected to task 
            cursor.execute("SELECT user_id FROM task_users WHERE task_id = %s", (task_id,))
            assigned_users = [row[0] for row in cursor.fetchall()]

            task_obj = Task(
                id=task_results[0],
                title=task_results[1],
                description=task_results[2],
                start_time=task_results[3],
                end_time=task_results[4],
                estimated_time=task_results[5],
                start_adress=task_results[6],
                destination_adress=task_results[7],
                status=task_results[8],
                car_ids=car_ids,
                assigned_users=assigned_users
            )
            return task_obj, 200
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
            sql_query=("SELECT id, title, description, start_time, end_time, estimated_time, start_adress, destination_adress, status FROM tasks")

            cursor.execute(sql_query)
            all_tasks_data = cursor.fetchall()

            tasks_list = []
            for task_data in all_tasks_data:
                task_id= task_data[0]
                task_obj, status_code = self._get_task_with_relations(task_id)

                if status_code == 200:
                    tasks_list.append(task_obj)
                else:
                    print(f" Kunde inte hämta fullständig data för task ID {task_id}: {task_obj['message']}")


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
            allwoed_status=['planerat', 'pågående', 'avbrutet', 'klart']

            car_ids_to_update = task_data.get('car_ids')
            assigned_users_to_update  = task_data.get('assigned_users')


            curent_task,curent_task_status_kod = self._get_task_with_relations(task_id)
            if curent_task_status_kod !=200:
                return curent_task, curent_task_status_kod 
            
            old_car_id = curent_task.car_ids if curent_task else[]
            old_assigned_users = curent_task.assigned_users if curent_task else []


            for key, value in task_data.items():
                if key == 'status' and value not in allwoed_status:
                    return {"message": f"Ogiltig status {value}. Tillåtna värden är {allwoed_status}"}, 400
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
            
                #count estimated time based of the given time or uppdated time
                if 'start_time' in task_data or 'end_time' in task_data:
                    new_start_time = datetime.datetime.fromisoformat(task_data.get('start_time', curent_task.start_time.isoformat()))
                    new_end_time = datetime.datetime.fromisoformat(task_data.get('end_time', curent_task.end_time.isoformat()))

                    if new_end_time <= new_start_time:
                        return {"message": "Sluttiden måste vara efter starttiden vid uppdatering."}, 400
                    new_estimated_time = int((new_end_time - new_start_time).total_seconds()/ 60 )
                    if 'estimated_time' not in task_data:
                        updated_fields.append("estimated_time = %s")
                        values.append(new_estimated_time)
                
                if not updated_fields and car_ids_to_update is None and assigned_users_to_update is None:
                    return curent_task, 200
                

                if updated_fields:

                    sql_query_task= f"UPDATE tasks SET {', '.join(updated_fields)} WHERE id = %s"
                    values.append(task_id)
                   
                    cursor.execute(sql_query_task, tuple(values))
                
                #uppdating car/vehicle 
                if car_ids_to_update is not None:
                    free_cars = set(old_car_id) - set(car_ids_to_update)

                    for car_id in free_cars:
                        cursor.execute("SELECT COUNT(*) FROM task_cars WHERE car_id = %s AND task_id !=%s", (car_id, task_id))

                        if cursor.fetchone()[0] == 0:
                            self.car_services.update_car(car_id, {'is_occupied': False})

                    #add new vehicle and uppdate is_occupied
                    car_to_free = set(car_ids_to_update) - set(old_car_id)
                    for car_id in car_to_free:
                        car, _= self.car_services.get_car_by_id(car_id)
                        if isinstance(car, dict) and 'message' in car:
                            raise ValueError(f"Fordon med ID {car_id} hittades inte för tilldelning.")
                        
                        
                        self.car_services.update_car(car_id, {'is_occupied': True})
                        cursor.execute("INSERT INTO task_cars (task:id, car_id) VALUES (%s, %s)", (task_id, car_id))


                    cars_to_remove= set(old_car_id) - set(car_ids_to_update)
                    for car_id in cars_to_remove:
                        cursor.execute("DELETE FROM task_cars WHERE task_id = %s AND car_id = %s", (task_id, car_id))

                #updatre user

                if assigned_users_to_update is not None:
                    user_to_free = set(old_assigned_users) - set(assigned_users_to_update)

                    for user_id in user_to_free:
                        cursor.execute(" SELECT COUNT(*) FROM task_users WHERE user_id = %s AND task_id != %s", (user_id, task_id))

                        if cursor.fetchone()[0] == 0:
                            self.user_services.update_user(user_id, {'is_occupied': False})
                    

                    user_to_assgin = set(assigned_users_to_update) - set(old_assigned_users)
                    for user_id in user_to_assgin:
                        user, user_status_kod = self.user_services.get_user_by_id(user_id)

                        if user_status_kod !=200 or not isinstance(user, User):
                            raise ValueError(f"Användare med ID {user_id} hittades inte för tilldelning.")
                        self.user_services.update_user(user_id, {'is_occupied': True})
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
        #caching validating error
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
                for car_id in task_to_delete.car_ids:
                    cursor.execute("""
                                    SELECT COUNT(*) FROM task_cars tc JOIN tasks t on tc.task_id = t.id
                                   WHERE tc.car_id = %s AND t.status IN ('planerat', 'pågående') AND tc.task_id != %s """, 
                                   (car_id, task_id))
                    
                    if cursor.fetchone()[0] == 0:
                        self.car_services.update_car(car_id, {'is_occupied': False})

                #changing is_occupied to all connected users
                for user_id in task_to_delete.assigned_users:
                    cursor.execute("""
                                    SELECT COUNT(*) FROM task_users tu JOIN tasks t on tu.task_id = t.id
                                   WHERE tu.user_id = %s AND t.status IN ('planerat', 'pågående') AND tu.task_id != %s """,
                                    (user_id, task_id))
                    
                    
                    if cursor.fetchone()[0] == 0:
                        self.user_services.update_user(user_id, {'is_occupied': False})

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