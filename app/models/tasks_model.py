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
    
    def __init__(self,
                  id:int,
                  title:str, 
                  description:str, 
                  car_id:int,
                    
                 start_adress:str,
                 destination_adress:str,
                 estimated_time:int, 
                 status:str ):
        self.id = id
        self.title = title
        self.description = description
        self.car_id = car_id
        
        self.start_adress = start_adress
        self.destination_adress=destination_adress
        self.estimated_time = estimated_time
        self.status = status
    
    
    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description':self.description,
            'estimated_time':self.estimated_time,
            'start_adress': self.start_adress,
            'status' : self.status,
            'destination_adress':self.destination_adress,
            'car_id': self.car_id,
        }