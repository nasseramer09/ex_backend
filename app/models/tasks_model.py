import datetime

class Task:

    id:int
    title:str
    description:str
    estimated_time:int
    start_adress:str
    destination_adress:str
    car_id = int
    status:str
    
    def __init__(self, id:int,title:str, description:str, estimated_time:str, status:str, start_adress:str, destination_adress:str, car_id:int):
        self.id = id
        self.title = title
        self.description = description
        self.estimated_time = estimated_time
        self.start_adress = start_adress
        self.status = status
        self.destination_adress=destination_adress
        self.car_id = car_id
    
    def title(self):
        return f"{self.title}"
    
    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description':self.description,
            'estimated_time':self.estimated_time,
            'start_adress': self.start_adress,
            'status' : self.status,
            'destination':self.destination,
            'car_id': self.car_id,
        }