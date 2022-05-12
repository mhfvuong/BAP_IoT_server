from tinydb import TinyDB, Query
from datetime import datetime
import serial
import io
import globals

#db = None
#user = None
#id_type = None
#data_format = None
        

def store_data(all_data):
    date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    data_type = globals.prop_id_translation[all_data[5]]
    sensor_data = globals.process_func[data_type](all_data[6])
    if globals.db.search(globals.User['Date'] == date):
        globals.db.update({data_type: sensor_data}, globals.User['Date'] == date)
    else:
        globals.db.insert({'Date': date, data_type: sensor_data})
    print(date, ' - ', data_type, ': ', sensor_data)


def main():
#    global id_type
#    global db
#    global user
#    global data_format
        
#    globals.prop_id_translation = {'0x75': 'Temperature', '0xa7': 'Humidity'}
#    globals.db = TinyDB('db.json')
#    globals.User = Query()
#    globals.process_func = {'Temperature': process_data, 'Humidity': process_data}

    ser = serial.Serial('/dev/ttyACM0',
                    baudrate=115200, timeout=0.1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    while True:
        text = sio.readline()
        print(text)
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
    globals.init()
    main()
    
