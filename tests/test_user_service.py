# import uuid
# import pytest 
# from app.services.user_services import User_Services
# from app.models.users_model import User
# from app.db import connectionToDataBase

# @pytest.fixture(scope="function")
# def db_connection():
#     conn = connectionToDataBase.DataBaseConnection.get_db_connection()
#     yield conn

#     if conn:
#         #for att ångra ev ändringar som görs under test
#         conn.rollback()
#         conn.close()

# @pytest.fixture
# def user_service(db_connection):
#     return User_Services()

# def test_create_account_success(user_service, db_connection):
#     username=f"user_{uuid.uuid4().hex[:8]}" #För att göra användarnamnet unikt 
#     user_data={
#         'first_name':'Test',
#         'last_name':'Testsson',
#         'username': username,
#         'password_hash':'teslösenord',
#         'role':'personal',
#         'phone_number':'0701234567'
#     }

#     new_user, status_code = user_service.createAccount(user_data)
#     assert status_code == 201
#     assert isinstance(new_user, User)
#     assert new_user.username == username

# def test_create_account_duplicate_username(user_service, db_connection):
#     username = f"user_{uuid.uuid4().hex[:8]}" 
#     existing_user_data ={
#         'first_name':'Test1',
#         'last_name':'Testsson1',
#         'username': username,
#         'password_hash':'teslösenord1',
#         'role':'admin',
#         'phone_number':'0701234567'
#     }

#     user_service.createAccount(existing_user_data)

#     duplicate_user = {
#         'first_name':'Test12',
#         'last_name':'Testsson12',
#         'username': 'userforTesT1',
#         'password_hash':'teslösenord12',
#         'role':'admin',
#         'phone_number':'0701234567'
#     }
#     result, status_code = user_service.createAccount(duplicate_user)
#     assert status_code == 400
#     assert isinstance(result, dict)
#     assert 'Användarnamnet är redan upptaget' in result['message']

# def test_get_user_by_id(user_service, db_connection):
#     username=f"user_{uuid.uuid4().hex[:8]}" 
#     test_user_data={
#         'first_name':'Test12',
#         'last_name':'Testsson12',
#         'username': 'userforTesT12',
#         'password_hash':username,
#         'role':'admin',
#         'phone_number':'0701234567'
#     }
#     created_user, _= user_service.createAccount(test_user_data)
#     retrived_user= user_service.get_user_by_id(created_user.id)
#     assert isinstance(retrived_user, User)
#     assert retrived_user.username == 'userforTesT12'

# def test_get_user_by_id_not_found(user_service, db_connection):
#     non_existing_user= user_service.get_user_by_id(1000)
#     assert non_existing_user is None

# def test_get_all_users(user_service, db_connection):
#     user_data1={
#          'first_name':'all_test_1',
#         'last_name':'all_son1',
#         'username': 'userforTesT13',
#         'password_hash':'all1234',
#         'role':'admin',
#         'phone_number':'0776543210'
#     }

#     user_data2={
#          'first_name':'all_test_2',
#         'last_name':'all_son2',
#         'username': 'userforTesT14',
#         'password_hash':'all1234e',
#         'role':'personal',
#         'phone_number':'0776543210'
#     }
#     user_service.createAccount(user_data1)
#     user_service.createAccount(user_data2)

#     all_users= user_service.get_all_users()
#     assert isinstance(all_users, list)
#     assert len(all_users) >= 2

# def test_update_user(user_service, db_connection):
#      username=f"user_{uuid.uuid4().hex[:8]}" 
#      user_data={
#          'first_name':'orginal',
#         'last_name':'namn',
#         'username': username,
#         'password_hash':'passpw',
#         'role':'personal',
#         'phone_number':'0776543210'
#     }
#      created_user, _= user_service.createAccount(user_data)

#      update_data = {'first_name':'Uppdaterad', 'phone_number': '456345'}

#      updated_user = user_service.update_user(created_user.id, update_data)
     
#      assert isinstance(updated_user, User)
#      assert updated_user.first_name == 'Uppdaterad'
#      assert updated_user.phone_number == '456345'
#      assert updated_user.username == username
     
# def test_update_user_not_found(user_service, db_connection):
#     update_data = {'first_name':'Testtesttest'}
#     non_existing_user = user_service.update_user(19999, update_data)
#     assert non_existing_user is None


# def test_delete_user(user_service, db_connection):
#      username=f"user_{uuid.uuid4().hex[:8]}" 
#      user_data={
#         'first_name':'användare',
#         'last_name':'som ska',
#         'username': username,
#         'password_hash':'passpw',
#         'role':'personal',
#         'phone_number':'0776543210'
#     }
#      create_user, _= user_service.createAccount(user_data)

#      delete_user = user_service.delete_user(create_user.id)
#      assert delete_user is True
#      assert user_service.get_user_by_id(create_user.id) is None

# def test_deleted_user_not_found(user_service, db_connection):
#     success_deletation = user_service.delete_user(9999)
#     assert success_deletation is False
     