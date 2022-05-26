import asyncio
from quart import Quart, render_template


class WebApp:
    app = None

    def __init__(self, name, db, publisher, todo):
        self.app = Quart(name)
        self.db = db
        self.publisher = publisher
        self.todo = todo

        self.app_task = None

        self.temp = 0
        self.hum = 0
        self.vol = 0

        publisher.sub_list['Temperature'].append(self.update_temp)
        publisher.sub_list['Humidity'].append(self.update_hum)
        publisher.sub_list['Audio'].append(self.update_vol)

        self.publisher.sub_list['Close'].append(self.exit)

    async def run(self):
        self.app_task = asyncio.create_task(self.app.run_task(host='0.0.0.0', port=80, debug=False))
        self.todo.add(self.app_task)
        self.app.add_url_rule('/', 'data_page', self.data_page, methods=['GET'])

    async def data_page(self):
        templatedata = {'title': 'Data page', 'temp': self.temp, 'hum': self.hum, 'vol': self.vol}
        return await render_template('test.html', **templatedata)

    async def update_temp(self):
        self.temp = self.db.get_most_recent('Temperature')

    async def update_hum(self):
        self.hum = self.db.get_most_recent('Humidity')

    async def update_vol(self):
        self.vol = self.db.get_most_recent('Audio')

    async def exit(self):
        self.app_task.cancel()
