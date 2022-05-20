from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
import asyncio

from analysis import Analysis


class GUI:
    def __init__(self, db, publisher, todo):
        self.db = db
        self.publisher = publisher
        self.todo = todo
        self.tasks = None
        self.analysis = Analysis(self.db)

        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.close_gui)

        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()

        ttk.Label(self.frm, text='Temperature: ..., Humidity: ...').grid(column=0, row=0)
        ttk.Button(self.frm, text='Exit', command=self.close_gui).grid(column=0, row=2)

        self.fig = Figure(figsize=(5, 4), dpi=100)

        #self.temp_plot = self.fig.add_subplot(211)
        #self.temp_plot.title.set_text('Temperature')
        #self.temp_plot.plot()
#
        #self.hum_plot = self.fig.add_subplot(212)
        #self.hum_plot.title.set_text('Humidity')
        #self.hum_plot.plot()

        self.avg_plot = self.fig.add_subplot(111)
        self.avg_plot.title.set_text('Average temperature')
        self.avg_plot.plot()

        self.canvas = FigureCanvasTkAgg(self.fig, self.frm)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=1)

        self.temp = [0]
        self.temp_time = ['0']

        self.hum = [0]
        self.hum_time = ['0']

        self.avg_temp = [0]
        self.avg_hum = [0]
        self.avg_time = ['0']

        publisher.sub_list['Temperature'].append(self.update_temp)
        publisher.sub_list['Humidity'].append(self.update_hum)

    async def run(self, loop):
        ttk.Label(self.frm, text=f'Temperature: {self.temp[-1]}, Humidity: {self.hum[-1]}').grid(column=0, row=0)

        #self.temp_plot.clear()
        #self.temp_plot.plot(self.temp_time, self.temp, color='r', label='Temperature')
        #self.temp_plot.title.set_text('Temperature')
#
        #self.hum_plot.clear()
        #self.hum_plot.plot(self.hum_time, self.hum, color='b', label='Humidity')
        #self.hum_plot.title.set_text('Humidity')

        self.avg_plot.clear()
        self.avg_plot.plot(self.avg_time, self.avg_temp)
        self.avg_plot.title.set_text('Average temperature')

        self.canvas.draw()
        self.root.update()

        await asyncio.sleep(0.1)

        if loop:
            self.run_task = asyncio.create_task(self.run(loop), name='gui_loop')
            self.todo.add(self.run_task)

    async def update_temp(self):
        if len(self.temp) >= 10:
            self.temp.pop(0)
        self.temp.append(self.db.get_most_recent('Temperature'))

        if len(self.temp_time) >= 10:
            self.temp_time.pop(0)
        self.temp_time.append(datetime.today().strftime('%M:%S'))

    async def update_hum(self):
        if len(self.hum) >= 10:
            self.hum.pop(0)
        self.hum.append(self.db.get_most_recent('Humidity'))

        if len(self.hum_time) >= 10:
            self.hum_time.pop(0)
        self.hum_time.append(datetime.today().strftime('%M:%S'))

    async def update_avg(self):
        if len(self.avg_temp) >= 10:
            self.avg_temp.pop(0)
        self.avg_temp.append(self.analysis.average('Temperature', 60))

        if len(self.avg_hum) >= 10:
            self.avg_hum.pop(0)
        self.avg_hum.append(self.analysis.average('Humidity', 60))

        if len(self.avg_time) >= 10:
            self.avg_time.pop(0)
        self.avg_time.append(datetime.today().strftime('%H:%M'))

    def close_gui(self):
        self.publisher.publish('Close')
        self.run_task.cancel()
        self.root.destroy()
