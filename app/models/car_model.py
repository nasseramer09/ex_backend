class Cars:
    id:int
    license_plate:str
    status:str

    def __init__(self, id:int, license_plate:str, status:str):
        self.id = id
        self.license_plate = license_plate
        self.status = status

    def get_car_id(self):
        return self.id
    
    def get_license_plate(self):
        return f"{self.license_plate}"

    def get_status(self):
        return f"{self.status}"
    
    def car_to_dic(self):
        return{
            'id': self.id,
            'license_plate': self.license_plate,
            'status': self.status
        }
    