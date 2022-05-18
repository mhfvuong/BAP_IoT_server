
class Preprocessing:
    def __init__(self):
        self.process_func = {'Temperature': self.divide, 'Humidity': self.divide}

    def divide(self, data):
        data = float(data)/100
        return data
