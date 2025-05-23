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
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        sql_query = (""" SELECT id, model, license_plate, status, is_occupied 
                     FROM cars 
                    """)
        cursor.execute(sql_query)
        result= cursor.fetchall()
        cursor.close()
        conn.close()

        car_list = []
        for row in result:
            car_list.append(Car(*row))
        return car_list, 200
    
    def update_car(self, car_id, car_data):
        conn = None
        cursor = None

        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()
            if not conn:
                return {"message": "Kunde inte ansluta till databasen"}, 500

            cursor = conn.cursor()
            updated_fields = []
            values = []
            allowed_status=['ledig', 'upptagen', 'ej i tjänst']

            for key, value in car_data.items():
                if key == 'status':
                    if value not in allowed_status:
                        return {"message": f"Ogiltig status '{value}'. Tillåtna värden är {', '.join(allowed_status)}"}, 400

                    updated_fields.append(f"{key} = %s")
                    values.append(value)
                elif key == 'license_plate':
                    updated_fields.append(f"{key} = %s")
                    values.append(value)

                elif key in ['model', 'is_occupied']:
                    updated_fields.append(f"{key} = %s")
                    values.append(value)
            
            if not updated_fields:
                car, status_kod = self.get_car_by_id(car_id)
                if isinstance(car, dict) and 'message' in car:
                    return car, status_kod
                return car, 200
            
            sql_query = f"UPDATE cars SET {', '.join(updated_fields)} WHERE id = %s"
            values.append(car_id)

            cursor.execute(sql_query, tuple(values))
            conn.commit()

            if cursor.rowcount ==0:
                return {"message": f"Kunde inte hitta fordon med ID {car_id} att uppdatera."}, 404
            return self.get_car_by_id(car_id)
            
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
                print(f"Fel vid uppdatering av fordon (databasfel): {e}")
            if "Duplicate entry" in str(e) and "license_plate" in str(e): 
                return {"message": "Registreringsnumret finns redan registrerat på ett annat fordon."}, 409
            
            return {"message": f"Fel vid uppdatering av fordon med id {car_id}: {e}"}, 500
        
        except Exception as e:
            if conn:
                conn.rollback()
            cursor.close()
            conn.close()
            error_message= f" Fel vid uppdatering av car med id: {car_id}: {e}"
            return {"message": error_message}, 500
        
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
       



      

    
    
