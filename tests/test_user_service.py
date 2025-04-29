import pytest 
from app.services.user_services import User_Services
from app.models.users_model import User
from db import connectionToDataBase

@pytest.fixture(scope="function")
def db_connection():
    conn = connectionToDataBase.DataBaseConnection.get_db_connection()
    yield conn

    if conn:
        #for att ångra ev ändringar som görs under test
        conn.rollback()
        conn.close()
@pytest.fixture
def user_service(db_connection):
    return User_Services

def test_create_account_success(user_service, db_connection):
    user_data={
        'first_name':'Test',
        'last_name':'Testsson',
        'username': 'test@testsson',
        'password_hash':'teslösenord',
        'role':'admin',
        'phone_number':'0701234567'
    }

    new_user, status_code = user_service.createAccount(user_data)
    assert status_code == 201
    assert isinstance(new_user, User)
    assert new_user.username == 'test@testsson'

def test_create_account_duplicate_username(user_service, db_connection):
    existing_user_data ={
        'first_name':'Test1',
        'last_name':'Testsson1',
        'username': 'test@testsson1',
        'password_hash':'teslösenord1',
        'role':'admin',
        'phone_number':'0701234567'
    }

    user_service.createAccount(existing_user_data)

    duplicate_user = {
         'first_name':'Test12',
        'last_name':'Testsson12',
        'username': 'test@testsson1',
        'password_hash':'teslösenord12',
        'role':'admin',
        'phone_number':'0701234567'
    }
    result, status_code = user_service.createAccount(duplicate_user)
    assert status_code == 400
    assert isinstance(result, dict)
    assert 'Användarnamnet är redan upptaget' in result['message']