import datetime
import pytest
from unittest.mock import MagicMock, patch
from app.services.user_services import User_Services
from app.models.users_model import User
from werkzeug.security import generate_password_hash

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_create_mock_test(mock_db_connection):
    services = User_Services()

    user_data={
        'first_name':'User',
        'last_name':'Test',
        'username': "testusertest",
        'password_hash':'testlösenord',
        'role':'personal',
        'phone_number':'0701234567',
        'email':'test@example.com'
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
                                        generate_password_hash('testlösenord'),
                                        'personal',
                                        '0701234567',
                                        datetime.datetime.now(),
                                        'test@example.com'
                                        )

    user_obj, status_kod= services.createAccount(user_data)

    assert status_kod == 201
    assert isinstance(user_obj, User)
    assert user_obj.username == "testusertest"
    assert user_obj.email == 'test@example.com'

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_get_user_by_id_mock_test(mock_db_connection):
    service = User_Services()

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1,
                                         'User',
                                         'Test',
                                        "testusertest",
                                        generate_password_hash('testlösenord'),
                                        'personal',
                                        '0701234567',
                                        datetime.datetime(2025, 1, 1),
                                        'test@example.com'
                                        )
    result = service.get_user_by_id(1)

    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "testusertest"
    assert result.email == 'test@example.com'

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_get_all_users_mock_test(mock_db_connection):
    fake_users = [
    (1, "Alice", "Test", "alicetest", "admin", "hash1", "0700000001", datetime.datetime(2024, 1, 1), 'alice@example.com'),
    (2, "Bob", "Demo", "bobdemo", "personal", "hash2", "0700000002", datetime.datetime(2024, 2, 1), 'bob@example.com'),
    (3, "Charlie", "Example", "charlieex", "kund", "hash3", "0700000003", datetime.datetime(2024, 3, 1), 'charlie@example.com'),
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
        assert isinstance(user, User)
        assert user.username == fake_users[i][3]
        assert user.email == fake_users[i][8]

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_user_update_mock_test(mock_db_connection):
    service = User_Services()
    mock_conn = MagicMock()
    mock_cursor=MagicMock()
    mock_conn.cursor.return_value= mock_cursor
    mock_db_connection.return_value = mock_conn

    updated_data = {
        "first_name": "UpdatedName",
        "last_name": "UpdatedLast",
        "role": "admin",
        "email": "updated@example.com"
    }

    mock_cursor.fetchone.return_value = (
        1,
        "UpdatedName",
        "UpdatedLast",
        "testusertest",
        "admin",
        "hash123",
        "0701234567",
        datetime.datetime(2025, 1, 1),
        "updated@example.com"
    )

    result = service.update_user(1, updated_data)
    assert isinstance(result, User)
    assert result.username ==  "testusertest"
    assert result.first_name == "UpdatedName"
    assert result.role == "admin"
    assert result.email == "updated@example.com"


@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_delete_user_mock_test(mock_db_connection):
    service = User_Services()
    mock_conn = MagicMock()
    mock_cursor=MagicMock()
    mock_conn.cursor.return_value= mock_cursor
    mock_db_connection.return_value = mock_conn

    mock_cursor.rowcount = 1
    result = service.delete_user(1)
    assert result == True

@patch('app.services.user_services.connectionToDataBase.DataBaseConnection.get_db_connection')
def test_get_user_by_email_mock_test(mock_db_connection):
    service = User_Services()

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1,
                                         'User',
                                         'Test',
                                         "testusertest",
                                         generate_password_hash('testlösenord'),
                                         'personal',
                                         '0701234567',
                                         datetime.datetime(2025, 1, 1),
                                         'test@example.com'
                                         )
    result = service.get_user_by_email('test@example.com')

    assert isinstance(result, User)
    assert result.id == 1
    assert result.username == "testusertest"
    assert result.email == 'test@example.com'

def test_verify_password_mock_test():
    service = User_Services()
    hashed_password = generate_password_hash('mysecretpassword')
    mock_user = User(
        id=1,
        first_name='Test',
        last_name='User',
        username='testuser',
        role='personal',
        password_hash=hashed_password,
        phone_number='1234567890',
        created_at=datetime.datetime.now(),
        email='test@example.com'
    )

    assert service.verify_password(mock_user, 'mysecretpassword') == True
    assert service.verify_password(mock_user, 'wrongpassword') == False
    assert service.verify_password(None, 'anypassword') == False