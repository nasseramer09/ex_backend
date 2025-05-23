from db.connectionToDataBase import DataBaseConnection
class Table_Creation:


    def create_users_table():
        connection = DataBaseConnection.get_db_connection()
        cursor=connection.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    first_name VARCHAR(50)  NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(50) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'personal') NOT NULL,
                    phone_number VARCHAR (50) NOT NULL,
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
                    status ENUM('ledig', 'upptagen', 'ej i tjänst') DEFAULT 'ledig',
                    is_occupied BOOLEAN DEFAULT FASLE
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
                            start_time DATETIME NOT NULL,
                            end_time DATETIME NOT NULL,
                            estimated_time INT,
                            start_adress VARCHAR(250) NOT NULL,
                            destination_adress VARCHAR(250) NOT NULL,
                            status ENUM('planerat', 'pågående', 'klart', 'avbrutet') DEFAULT 'planerat'
                            )CHARSET=utf8mb4
                    """)
        connection.commit()
        cursor.close()
        connection.close()
        




    def create_task_cars_table():
        connection = DataBaseConnection.get_db_connection()

        cursor = connection.cursor()

        cursor.execute(""" CREATE TABLE IF NOT EXISTS task_cars(
                       task_id INT NOT NULL,
                       car_id  INT NOT NULL,
                       PRIMARY KEY (task_id, car_id), -- To prevent doubble
                       FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, --Deletes relations after deletation
                       FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
                       
                       
                       )"""
                    )
        connection.commit()
        cursor.close()
        connection.close()


    def create_task_users_table():
        connection = DataBaseConnection.get_db_connection()

        cursor = connection.cursor()

        cursor.execute(""" CREATE TABLE IF NOT EXISTS task_users(
                       task_id INT NOT NULL,
                       user_id  INT NOT NULL,
                       PRIMARY KEY (task_id, user_id), 
                       FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                       
                       
                       )"""
                    )
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def create_All_Tables():
        Table_Creation.create_users_table()
        Table_Creation.create_cars_table()
        Table_Creation.create_tasks_table()
        Table_Creation.create_task_cars_table()
        Table_Creation.create_task_users_table()
        print("All tables has been created!")
