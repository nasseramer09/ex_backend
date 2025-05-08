import mysql
from ..db import connectionToDataBase
from app.models.car_model import Cars

class Car_services:
    def insert_car(self, car_data):
        conn = None
        cursor = None
        try:
            conn = connectionToDataBase.DataBaseConnection.get_db_connection()

            if not conn:
                return None, 500
            
            cursor = conn.cursor()

            sql_query=""" INSERT INTO cars (model, license_plate, status)
                        VALUES (%s, %s, %s)
                    """
            values = (
                car_data.get('model'),
                car_data.get('license_plate'),
                car_data.get('status')
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
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        sql_query = (""" SELECT id, model, license_plate, status 
                     FROM cars WHERE id = %s 
                    """)
        cursor.execute(sql_query, (car_id,))
        result= cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return Cars(*result), 200
        return {"message": f"Kunde inte hotta ett fordon med id: {car_id} "}, 404
    
    def get_all_cars(self):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        sql_query = (""" SELECT id, model, license_plate, status 
                     FROM cars 
                    """)
        cursor.execute(sql_query)
        result= cursor.fetchall()
        cursor.close()
        conn.close()

        car = []
        for row in result:
            car.append(Cars(*row))
        return car, 200
    
    def update_car(self, car_id, car_data):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        updated_fields = []
        values = []
        allowed_status=['ledig', 'upptaget', 'ej i tjänst']

        for key, value in car_data.items():
            if key == 'status' and value not in allowed_status:
                cursor.close()
                conn.close()
                return {"message": f"Ogiltig status {value}. Tillåtna värden är {allowed_status}"}, 400
            updated_fields.append(f"{key} = %s")
            values.append(value)
        
        if not updated_fields:
            car, status_kod = self.get_car_by_id(car_id)
            cursor.close()
            conn.close()
            return car, status_kod
        
        sql_query = f"UPDATE cars SET {', '.join(updated_fields)} WHERE id = %s"
        values.append(car_id)

        try:
            cursor.execute(sql_query, tuple(values))
            conn.commit()
            cursor.close()
            conn.close()
            return self.get_car_by_id(car_id)
        except Exception as e:
            if conn:
                conn.rollback()
            cursor.close()
            conn.close()
            error_message= f" Fel vid uppdatering av car med id: {car_id}: {e}"
            return {"message": error_message}, 500
        
    def delete_car(slef, car_id):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute( " DELETE FROM cars WHERE id = %s", (car_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"message": f" car med id {car_id} har tagits bort"}
            else:
                return {"message": f"Kunde inte hitta car med id {car_id} för att ta bort "}, 404
            
        except Exception as e:
            if conn:
                conn.rollback()
                return{"message": f"Något blev fel vid bortagandet av car med id {car_id}: {e}"}, 500
            
        finally:
            cursor.close()
            conn.close()
       



      

    
    
