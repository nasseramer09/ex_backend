class Cars:
    id:int
    model:str
    license_plate:str
    status:str

    def __init__(self, id:int, model:str, license_plate:str, status:str):
        self.id = id
        self.model = model
        self.license_plate = license_plate
        self.status = status

    def get_car_id(self):
        return self.id
    
    def to_dic(self):
        return{
            'id': self.id,
            'model': self.model,
            'license_plate': self.license_plate,
            'status': self.status
        }
    