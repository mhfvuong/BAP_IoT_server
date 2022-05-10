import datetime
from tinydb import TinyDB, Query


def get_data(datab, qry, datatype=None):
    '''
    input:
    datab = database, qry = Query, datatype = what data it wants
    takes the data logged from 10 seconds ago and returns it
    '''
    date = datetime.date.today().strftime('%d-%m-%Y %H:%M:')
    seconds = int(datetime.date.today().strftime('%S')) - 10
    date += str(seconds)
    requested_data = datab.search(qry.date == date)
    temperature = None
    humidity = None
    for data in requested_data:
        if datatype is not None:
            return data[datatype]
        if data['Temperature']:
            temperature = data['Temperature']
        if data['Humidity']:
            humidity = data['Humidity']
    return [temperature, humidity]


if __name__ == '__main__':
    db = TinyDB('db.json')
    qr = Query()
    get_data(db, qr)
