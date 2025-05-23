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
     
    def __init__(self, id:int,first_name:str, last_name:str, username:str, role:str, password_hash:str, phone_number:str, created_at:datetime, email:str, is_occupied:bool=False):
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

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def user_to_dic(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name':self.last_name,
            'username':self.username,
            'role': self.role,
            'phone_number' : self.phone_number,
            'email' : self.email,
            'created_at':self.created_at,
            'is_occupied':self.is_occupied
        }