import datetime

class User:

    id:int
    firstname:str
    lastname:str
    username:str
    role:str
    password_hash:str
    phone_number:str
    created_at:datetime
     
    def __init__(self, id:int,firstname:str, lastname:str, username:str, role:str, password_hash:str, phone_number:str, created_at:datetime):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.phone_number = phone_number
        self.created_at = created_at
    
    def full_name(self):
        return f"{self.firstname} + {self.lastname}"
    
    def user_to_dic(self):
        return {
            'id': self.id,
            'first_name': self.firstname,
            'last_name':self.lastname,
            'username':self.username,
            'role': self.role,
            'phone_number' : self.phone_number,
            'created_at':self.created_at
        }