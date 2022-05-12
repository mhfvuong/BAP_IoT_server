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
        try:
            r_data = requested_data[datatype]
            return r_data
        except Exception as e:
            print(e)
            return 0
    else:
        return None
        
        
def get_most_recent(datatype=None):
    last_id = len(globals.db)
    for i in range(last_id):
        if datatype in globals.db.get(doc_id=(last_id-i)):
            return globals.db.get(doc_id=last_id-i)[datatype]
    return None
        

if __name__ == '__main__':
    get_data(datatype='Temperature')
