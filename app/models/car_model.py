class Car:
    id:int
    model:str
    license_plate:str
    status:str
    is_occupied: bool = False

    def __init__(self, id:int, model:str, license_plate:str, status:str, is_occupied:bool=False):
        self.id = id
        self.model = model
        self.license_plate = license_plate
        self.status = status
        self.is_occupied=is_occupied

    def get_car_id(self):
        return self.id
    
    def to_dic(self):
        return{
            'id': self.id,
            'model': self.model,
            'license_plate': self.license_plate,
            'status': self.status,
            'is_occupied':self.is_occupied
        }
    