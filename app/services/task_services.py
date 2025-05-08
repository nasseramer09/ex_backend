from ..db import connectionToDataBase
from app.models.tasks_model import Task

class Task_services:
    def create_task(self, task_data):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()

        if not conn:
            return None, 500

        cursor = conn.cursor()

        sql_query="""
                    INSERT INTO tasks (title, description, car_id, start_adress, destination_adress, estimated_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
        values = (
            task_data.get('title'),
            task_data.get('description'),
            task_data.get('car_id'),
            task_data.get('start_adress'),
            task_data.get('destination_adress'),
            task_data.get('estimated_time'),
            task_data.get('status', 'planerat')
            )
        try:
            cursor.execute(sql_query, values)
            conn.commit()
            task_id=cursor.lastrowid
            cursor.close()
            conn.close()
            return self.get_task_by_id(task_id), 201
        except Exception as e:
            if conn:
                conn.rollback()
            cursor.close()
            conn.close()
            print(f"Fel vid skapandet av task: {e}")
            if "Duplicate entry" in str(e):
              return {"message": f"En task med liknande data finns redan"}, 400
            else:
              return {"message": f"Något blev fel vid skapandet av tasken {e}"}, 500
            
    def get_task_by_id(self, task_id):
        conn= connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, car_id, start_adress, destination_adress, estimated_time, status" \
                        " FROM tasks WHERE id = %s", (task_id,)
                        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return Task(*result), 200
        return {"message": f"Kunde inte hitta uppgifter med id: {task_id}"}, 404

    def get_all_tasks(self):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        sql_query=("SELECT id, title, description, estimated_time, start_adress, destination_adress, car_id, status" \
        " FROM tasks")

        cursor.execute(sql_query)

        result = cursor.fetchall()
        cursor.close()
        conn.close()

        task = []
        for row in result:
            task.append(Task(*row))
        return task, 200
    
    def update_task(self, task_id, task_data):
        conn = connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor = conn.cursor()
        updated_fields = []
        values = []
        allwoed_status=['planerat', 'pågående', 'klart']

        for key, value in task_data.items():
            if key == 'status' and value not in allwoed_status:
                cursor.close()
                conn.close()
                return {"message": f"Ogiltig status {value}. Tillåtna värden är {allwoed_status}"}, 400
            
            updated_fields.append(f"{key} = %s")
            values.append(value)
        
        if not updated_fields:
            cursor.close()
            conn.close()
            return self.get_task_by_id(task_id)
        
        sql_query= f"UPDATE tasks SET {', '.join(updated_fields)} WHERE id = %s"
        values.append(task_id)

        try:
            cursor.execute(sql_query, tuple(values))
            conn.commit()
            cursor.close()
            conn.close()
            return self.get_task_by_id(task_id)
        
        except Exception as e:
            if conn:
                conn.rollback()
            cursor.close()
            conn.close()
            error_message= f"Fel vid uppdatering av tasken med id: {task_id}: {e}"
            return {"message": error_message}, 500
            
    def delete_task(self, task_id):
        conn=connectionToDataBase.DataBaseConnection.get_db_connection()
        cursor= conn.cursor()

        try:
            cursor.execute(" DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"message": f" uppgift med id {task_id} har tagits bort"}, 204
            else:
                return {"message": f" Kunde inte hitta uppgift med id {task_id} för at ta bort"}, 404

        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Fel vid borttagandet av tasken: {e}")
                return {"message": "Något blev fel vi borttagandet av uppgiften med id {task_id}: {e} "}, 500

        finally:
            cursor.close()
            conn.close()