from tinydb import TinyDB
import globals


def get_data(datatype=None):
    '''
    input:
    datab = database, datatype = what data it wants
    Needs a datatype to return most recently logged data
    '''
    d_id = globals.db.all()[-1].doc_id
    requested_data = globals.db.get(doc_id=d_id)
    if datatype:
        return requested_data[datatype]
    else:
        return None

if __name__ == '__main__':
    get_data(datatype='Temperature')
