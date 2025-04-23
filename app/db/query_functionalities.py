from db.connectionToDataBase import DataBaseConnection
class Query_functionalities:
    def get_users(self):
        connectionToDB = DataBaseConnection.get_db_connection()
        cursor = connectionToDB.cursor(dictionary=True)
        str_query=f"""
            SELECT first_name,
                  last_name,
                  username, role,
                    created_at
                FROM
                  users;
                """
        
        cursor.execute(str_query)
        user_Data=cursor.fetchall()
        cursor.close()
        connectionToDB.close()
        return user_Data