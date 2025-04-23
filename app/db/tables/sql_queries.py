from db.connectionToDataBase import DataBaseConnection
class Table_Creation:


    def create_users_table():
        connection = DataBaseConnection.get_db_connection()
        cursor=connection.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    first_name VARCHAR(50)  NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR (50) NOT NULL,
                    role ENUM('admin', 'personal') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
        connection.commit()
        cursor.close()
        connection.close()

    def create_cars_table():
        connection = DataBaseConnection.get_db_connection()
        cursor=connection.cursor()

        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cars(
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    model VARCHAR(50),
                    license_plate VARCHAR(10) UNIQUE NOT NULL, 
                    status ENUM('ledig', 'upptaget', 'ej i tjänst') DEFAULT 'ledig'
                    
                    )
                    """)
        connection.commit()
        cursor.close()
        connection.close()


    def create_tasks_table():
        connection = DataBaseConnection.get_db_connection()
        cursor=connection.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks(
                            id INT AUTO_INCREMENT PRIMARY KEY, 
                            title VARCHAR(250) NOT NULL,
                            description TEXT,
                            car_id INT,
                            start_adress VARCHAR(250) NOT NULL,
                            destination_adress VARCHAR(250) NOT NULL,
                            estimated_time INT,
                            status ENUM('planerat', 'pågående', 'klart') DEFAULT 'planerat',
                            FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE SET NULL
                            )CHARSET=utf8mb4
                    """)
        connection.commit()
        cursor.close()
        connection.close()
        
    @staticmethod
    def create_All_Tables():
        Table_Creation.create_users_table()
        Table_Creation.create_cars_table()
        Table_Creation.create_tasks_table()
        print("All tables has being created!")



