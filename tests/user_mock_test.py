import datetime
import pytest
from unittest.mock import MagicMock, patch
from app.services.user_services import User_Services
from models.users_model import User

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def create_mock_test(mock_db_connection):
    services = User_Services()

    user_data={
        'first_name':'User',
        'last_name':'Test',
        'username': "testusertest",
        'password_hash':'testlösenord',
        'role':'personal',
        'phone_number':'0701234567'
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_connection.return_value = mock_conn

    mock_cursor.lastrowid = 1

    mock_cursor.fetchone.return_value = (1, 
                                         'User', 
                                         'Test', 
                                        "testusertest",
                                        'testlösenord', 
                                        'personal',
                                        '0701234567')
    
    user_obj, status_kod= services.createAccount(user_data)

    assert status_kod == 201
    assert isinstance(user_obj, User)
    assert user_obj.username == "testusertest"

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def get_user_by_id_mock_test(mock_db_connection):
    service = User_Services()

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1, 
                                         'User', 
                                         'Test', 
                                        "testusertest",
                                        'testlösenord', 
                                        'personal',
                                        '0701234567',
                                        datetime.datetime(2025, 1, 1)
                                        )
    result = service.get_user_by_id(1)

    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "testusertest"

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def get_all_users_mock_test(mock_db_connection):
    fake_users = [
    (1, "Alice", "Test", "alicetest", "admin", "hash1", "0700000001", datetime.datetime(2024, 1, 1)),
    (2, "Bob", "Demo", "bobdemo", "personal", "hash2", "0700000002", datetime.datetime(2024, 2, 1)),
    (3, "Charlie", "Example", "charlieex", "kund", "hash3", "0700000003", datetime.datetime(2024, 3, 1)),
    ]

    

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_connection.return_value = mock_conn


    mock_cursor.fetchall.return_value = fake_users

    service = User_Services()
    result = service.get_all_users()

    assert isinstance(result, list)
    assert len(result) ==  3
    for i, user in enumerate(result):
        assert isinstance(result, User)
        assert user.username == fake_users[i][3]


    