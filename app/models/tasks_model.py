import datetime

class Task:

    id:int
    title:str
    description:str
    start_time:datetime.datetime
    end_time:datetime.datetime
    estimated_time:int
    start_adress:str
    destination_adress:str
    car_ids = list[int]
    assigned_users = list[int]
    status:str
    
    def __init__(self,
                  id:int,
                  title:str, 
                  description:str, 
                  start_time:datetime.datetime,
                  end_time:datetime.datetime,
                  start_adress:str,
                  destination_adress:str,
                  car_ids:list[int],
                  assigned_users:list[int],
                 estimated_time:int, 
                 status:str ):
        self.id = id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.car_ids = car_ids
        self.assigned_users = assigned_users
        self.start_adress = start_adress
        self.destination_adress=destination_adress
        self.estimated_time = estimated_time
        self.status = status
    
    
    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description':self.description,
            'start_time':self.start_time.isoformat() if isinstance(self.start_time, datetime.datetime) else str(self.start_time),
            'end_time':self.start_time.isoformat() if isinstance(self.end_time, datetime.datetime) else str(self.end_time),
            'estimated_time':self.estimated_time,
            'start_adress': self.start_adress,
            'status' : self.status,
            'destination_adress':self.destination_adress,
            'car_id': self.car_ids,
            'assigned_users':self.assigned_users, 
        }