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
        self.gui_tasks = [None, None]
        self.analysis = Analysis(self.db)

        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.close_gui)

        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()

        ttk.Label(self.frm, text='Temperature: ..., Humidity: ..., Volume: ...').grid(column=0, row=0)
        ttk.Button(self.frm, text='Exit', command=self.close_gui).grid(column=0, row=2)

        self.fig = Figure(figsize=(5, 4), dpi=100)

        self.avg_plot = self.fig.add_subplot(111)
        self.avg_plot.title.set_text('Average temperature and humidity')
        self.avg_plot.set_xlabel('Time [H:M]')
        self.avg_plot.set_ylabel('Magnitude')
        self.avg_plot.plot()

        self.canvas = FigureCanvasTkAgg(self.fig, self.frm)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=1)

        self.temp = [0]
        self.temp_time = ['0']

        self.hum = [0]
        self.hum_time = ['0']

        self.audio = 0

        self.avg_temp = [0]
        self.avg_hum = [0]
        self.avg_time = ['0']

        publisher.sub_list['Temperature'].append(self.update_temp)
        publisher.sub_list['Humidity'].append(self.update_hum)
        publisher.sub_list['Audio'].append(self.update_audio)

    async def run(self):
        self.gui_tasks[0] = asyncio.create_task(self.run_loop(), name='gui_loop')
        self.todo.add(self.gui_tasks[0])

        self.gui_tasks[1] = asyncio.create_task(self.update_avg(), name='avg_graph_loop')
        self.todo.add(self.gui_tasks[1])

    async def run_loop(self):
        ttk.Label(self.frm, text=f'Temperature: {self.temp[-1]}, '
                                 f'Humidity: {self.hum[-1]}, '
                                 f'Volume: {self.audio}').grid(column=0, row=0)

        self.avg_plot.clear()
        self.avg_plot.plot(self.avg_time, self.avg_temp, color='r', label='Temperature')
        self.avg_plot.plot(self.avg_time, self.avg_hum, color='b', label='Humidity')
        self.avg_plot.set_xlabel('Time [H:M]')
        self.avg_plot.set_ylabel('Magnitude')
        self.avg_plot.title.set_text('Average temperature and humidity')
        self.avg_plot.legend()

        self.canvas.draw()
        self.root.update()

        await asyncio.sleep(0.1)

        self.gui_tasks[0] = asyncio.create_task(self.run_loop(), name='gui_loop')
        self.todo.add(self.gui_tasks[0])

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

    async def update_audio(self):
        self.audio = self.db.get_most_recent('Audio')

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

        await asyncio.sleep(60)
        self.gui_tasks[1] = asyncio.create_task(self.update_avg(), name='avg_graph_loop')
        self.todo.add(self.gui_tasks[1])

    def close_gui(self):
        self.publisher.publish('Close')
        for task in self.gui_tasks:
            task.cancel()
        self.root.destroy()
