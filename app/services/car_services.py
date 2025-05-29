import mysql
import mysql.connector
from ..db import connectionToDataBase
from app.models.car_model import Car

class Car_services:
    def insert_car(self, car_data):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            
            cursor = conn.cursor()

            sql_query=""" INSERT INTO cars (model, license_plate, status, is_occupied)
                        VALUES (%s, %s, %s, %s)
                    """
            values = (
                car_data.get('model'),
                car_data.get('license_plate'),
                car_data.get('status', 'ledig'),
                car_data.get('is_occupied', False)
            )
        
            cursor.execute(sql_query, values)
            conn.commit()
            car_id=cursor.lastrowid

            new_car, status_kod = self.get_car_by_id(car_id)
            return new_car, 201
        
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            print(f"Fel vid skapandet av car (databse fel): {e}")

            if "Duplicate entry" in str(e):
                return {"message": "Fordon med liknande data finns redan"}, 400
            else:
                return{"message": f"Något blev fel vid skapandet av fordon {e}"}, 500
   
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Något gick fel  {e}")
            return {"message": "Något belv fel vid skapandet av fordonet "}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:    
                conn.close()
            

    def get_car_by_id(self, car_id):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            sql_query = (""" SELECT id, model, license_plate, status, is_occupied 
                     FROM cars WHERE id = %s 
                    """)
            cursor.execute(sql_query, (car_id,))
            result= cursor.fetchone()


            if result:
                return Car(*result), 200
            return {"message": f"Kunde inte hitta fordon med id: {car_id} "}, 404
    
        except Exception as e:
            print(f"Fel vid hämtning av fordon med id {car_id}: {e}")
            return {"message": f"Kunde inte hämta fordonet med id: {car_id} på grund av ett fel: {e}"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all_cars(self):
        conn=None
        cursor=None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500
            
            cursor = conn.cursor()
            sql_query = (""" SELECT id, model, license_plate, status, is_occupied 
                        FROM cars 
                        """)
            cursor.execute(sql_query)
            result= cursor.fetchall()

            car_list = []
            for row in result:
                car_list.append(Car(*row))
            return car_list, 200
        
        except Exception as e:
            print(f"Fel vid hämtning av alla fordon: {e}")
            return {"message": f"Kunde inte hämta alla fordon på grund av ett fel: {e}"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_car_internal(self, car_id, car_data, existing_cursor=None):
        conn = None
        local_cursor = None

        try:
            if existing_cursor is None:
                conn = connectionToDataBase.DataBaseConnection.get_db_connection()
                local_cursor = conn.cursor()
                cursor_to_use = local_cursor
            else:
                cursor_to_use = existing_cursor
            
            updated_fields = []
            values = []
           

            for key, value in car_data.items():
                if key in ['model', 'license_plate', 'status', 'is_occupied']:
                    updated_fields.append(f"{key} = %s")
                    values.append(value)

            
            if not updated_fields:
                curent_car, status_kod = self.get_car_by_id(car_id)
                if status_kod ==200:
                    return curent_car, 200
                else:
                    return {"message":"Inga fält att uppdatera"}, 400
            
            sql_query = f"UPDATE cars SET {', '.join(updated_fields)} WHERE id = %s"
            values.append(car_id)

            cursor_to_use.execute(sql_query, tuple(values))

            if existing_cursor is None:
                conn.commit()
                updated_car, status_kod = self.get_car_by_id(car_id)
                if status_kod ==200:
                    return updated_car, 200
                else:
                    return updated_car, status_kod
            else:
                return {"message": "Fordonet har uppdaterats internt"},200


        except mysql.connector.Error as e:
            if conn and existing_cursor is None:
                conn.rollback()
                print(f"Fel vid uppdatering av fordon (databasfel): {e}")
                return {"message": f"Fel vid uppdatering av fordon med id {car_id}: {e}"}, 500

        except Exception as e:
            if conn and existing_cursor is None:
                conn.rollback()
            print(f"Något gick fel vid uppdatering av car med id: {car_id}: {e}")
            return {"message": f"Något blev fel vid uppdatering av car med id: {car_id}: {e}"}, 500
        
        finally:
            if local_cursor:
                local_cursor.close()
            if conn:
                conn.close()
    
    def update_car(self, car_id, data):
        return self.update_car_internal(car_id, data, existing_cursor=None)
        
    def delete_car(self, car_id):

        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500


            cursor = conn.cursor()

           
            cursor.execute( """ 
                            SELECT COUNT (*) FROM task_cars tc JOIN tasks t ON tc.task_id = t.id
                            WHERE  tc.car_id = %s AND t.status IN ('planerat', 'pågående')""", (car_id,))
                
            active_tasks_count = cursor.fetchone()[0]
                

            if active_tasks_count > 0:
                    return {"message": f" Kunde inte ta bort fordon med id {car_id}, Den är kopplat till {active_tasks_count} pågående eller planerade uppdrag"}, 409 
                
            cursor.execute("DELETE FROM cars WHERE id =%s", (car_id,))
            conn.commit()

            if cursor.rowcount > 0:
                    return {"message": f"Frodon med id {car_id} har tagits bort "}, 200
            else:
                    return {"message": f"Kunde inte hitta car med id {car_id} för att ta bort "}, 404
        except mysql.connector.errors:
            if conn:
                conn.rollback()  
                print(f"Fel vid borttagandet av fordon med id {car_id} (databasfel): {e}")
                return {"message": f"Något blev fel vid borttagandet av fordon med id {car_id}: {e}"}, 500
              
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Något blev fel vid bortagandet av fordon med id{car_id}: {e}")
                return{"message": f"Något blev fel vid bortagandet av car med id {car_id}: {e}"}, 500
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
       



      

    
    
