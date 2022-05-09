from tinydb import TinyDB, Query
from datetime import datetime
import serial
import io

db = None
user = None
id_type = None
data_format = None
        

def store_data(all_data):
    date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    data_type = id_type[all_data[5]]
    sensor_data = data_format[data_type](all_data[6])
    db.insert({'Date': date, data_type: sensor_data})
    print(date, ' - ', data_type, ': ', sensor_data)


def process_data(data):
    data = str(float(data)/100)
    return data


def main():
    global id_type
    global db
    global user
    global data_format
        
    id_type = {'0x75': 'Temperature', '0xa7': 'Humidity'}
    db = TinyDB('db.json')
    user = Query()
    data_format = {'Temperature': process_data, 'Humidity': process_data}

    ser = serial.Serial('/dev/ttyACM0',
                    baudrate=115200, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    while True:
        text = sio.readline()
        # split based on spaces
        # searh for DATA specifications
        # do fun stuff
        all_data = text.split()
        #print(all_data, '\n')
        for entry in all_data:
            if entry == 'DATA:' and len(all_data) > 6:
                print('found data:')
               # print(all_data, '\n')
                store_data(all_data)


if __name__ == '__main__':
    main()
    