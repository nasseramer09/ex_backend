import mysql.connector
import os

# class DataBaseConnection:

#     @staticmethod
#     def get_db_connection():
#         try:
        
#             connection = mysql.connector.connect(
#                 host=os.getenv("DB_HOST", "localhost"),
#                 user= os.getenv("DB_USER", "root"),
#                 password= os.getenv("DB_PASSWORD",""),
#                 database= os.getenv("DB_NAME", "uppdragshanteraren_db")
#                 )
#             print(f"databaseAnslutning lyckades")
#             return connection
#         except mysql.connector.Error as e:
#             print(f"Fel vid databaseAnslutning: {e}")
#             return None


      
class DataBaseConnection:
    _db_connection = None

    @classmethod
    def get_db_connection(cls):
        if cls._db_connection is None:
            try:
                cls._db_connection = mysql.connector.connect(
                    host=os.environ.get('DB_HOST'),
                    port=int(os.environ.get('DB_PORT')),
                    user=os.environ.get('MYSQL_USER'),
                    password=os.environ.get('MYSQL_PASSWORD'),
                    database=os.environ.get('MYSQL_DATABASE')
                )
                print("DatabaseAnslutning lyckades")
            except mysql.connector.Error as err:
                print(f"Fel vid databasanslutning: {err}")
                return None
        return cls._db_connection
