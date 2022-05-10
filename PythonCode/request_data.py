import datetime
from tinydb import TinyDB


def get_data(datab, datatype=None):
    '''
    input:
    datab = database, qry = Query, datatype = what data it wants
    takes the data logged from 10 seconds ago and returns it
    '''
    d_id = datab.all()[-1].doc_id
    requested_data = datab.get(doc_id=d_id)
    if datatype:
        return requested_data[datatype]
    else:
        return None

if __name__ == '__main__':
    db = TinyDB('db.json')
    get_data(db, datatype='Temperature')
