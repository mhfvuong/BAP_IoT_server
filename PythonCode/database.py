from tinydb import TinyDB, Query
from datetime import datetime


class Database:
    def __init__(self):
        self.db = TinyDB('data/testdb')
        self.db.truncate()
        self.User = Query()

    def store(self, data_type, data):
        date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        self.db.upsert({'Date': date, data_type: data}, self.User.Date == date)
        print(date, ' - ', data_type, ': ', data)

    def get_data(self, datatype=None):
        """
        input:
        datatype = what data it wants
        Needs a datatype to return most recently logged data
        """
        d_id = self.db.all()[-1].doc_id
        requested_data = self.db.get(doc_id=d_id)
        if datatype:
            try:
                r_data = requested_data[datatype]
                return r_data
            except Exception as e:
                print(e)
                return 0
        else:
            return None

    def get_most_recent(self, datatype=None):
        last_id = len(self.db)
        for i in range(last_id):
            if datatype in self.db.get(doc_id=(last_id-i)):
                return self.db.get(doc_id=last_id-i)[datatype]
        return None
