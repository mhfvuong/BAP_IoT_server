from tinydb import TinyDB, Query

db = None
User = None
prop_id_translation = None
process_func = None
todo = None


def init():
    global db
    global User
    global prop_id_translation
    global process_func
    global todo
    
    db = TinyDB('testdb.json')
    db.truncate()
    User = Query()
    prop_id_translation = {'0x75': 'Temperature', '0xa7': 'Humidity'}
    process_func = {'Temperature': divide, 'Humidity': divide}
    todo = set()


def divide(data):
    data = float(data)/100
    return data
