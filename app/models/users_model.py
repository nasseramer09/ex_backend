import datetime

class User:
    id:int
    first_name:str
    last_name:str
    username:str
    password_hash:str
    role:str
    created_at:datetime.datetime
    phone_number:str
    email:str
    is_occupied: bool = False
    assigned_tasks: list = []

    def __init__(self, id:int,first_name:str, last_name:str, username:str, role:str, password_hash:str, phone_number:str, created_at:datetime, email:str, is_occupied:bool=False, assigned_tasks:list=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.phone_number = phone_number
        self.created_at = created_at
        self.email=email
        self.is_occupied=is_occupied
        self.assigned_tasks = assigned_tasks if assigned_tasks is not None else []

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def user_to_dic(self, include_tasks: bool = False):
        user_dict = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name':self.last_name,
            'username':self.username,
            'role': self.role,
            'phone_number' : self.phone_number,
            'email' : self.email,
            'created_at':self.created_at.isoformat() if self.created_at else None,
            'is_occupied':self.is_occupied
        }
        if include_tasks:
            user_dict['assigned_tasks'] = self.assigned_tasks
        return user_dict