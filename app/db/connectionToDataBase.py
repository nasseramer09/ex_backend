import mysql.connector
import os

class DataBaseConnection:

    @staticmethod
    def get_db_connection():
        try:
        
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user= os.getenv("DB_USER", "root"),
                password= os.getenv("DB_PASSWORD",""),
                database= os.getenv("DB_NAME", "uppdragshanteraren_db")
                )
            print(f"databaseAnslutning lyckades")
            return connection
        except mysql.connector.Error as e:
            print(f"Fel vid databaseAnslutning: {e}")
            return None