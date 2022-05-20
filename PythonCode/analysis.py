from datetime import datetime, timedelta


class Analysis:
    def __init__(self, db):
        self.db = db

    def average(self, datatype: str, period: int):
        total = 0
        count = 0

        time = (datetime.today()-timedelta(seconds=period)).strftime('%d-%m-%Y %H:%M:%S')
        for entry in self.db.db.search(self.db.User.Date >= time):
            if datatype in entry:
                total += float(entry[datatype])
                count += 1

        if count != 0:
            return total/count
        return None
