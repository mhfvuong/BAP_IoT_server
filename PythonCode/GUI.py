import tkinter
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
import asyncio
import re

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

        self.dataLabel = ttk.Label(self.frm, text='Temperature: ..., Humidity: ...')
        self.dataLabel.grid(column=0, row=0)
        ttk.Button(self.frm, text='Exit', command=self.close_gui).grid(column=0, row=4)

        self.fig = Figure(figsize=(5, 4), dpi=100)

        self.avg_plot = self.fig.add_subplot(111)
        self.avg_plot.title.set_text('Average temperature and humidity')
        self.avg_plot.set_xlabel('Time [H:M]')
        self.avg_plot.set_ylabel('Magnitude')
        self.avg_plot.plot()

        self.questionCanvas = Canvas(self.frm, height=10, width=10)
        self.questionIndicator = self.questionCanvas.create_oval(0, 0, 10, 10, fill='#000fff000')
        self.questionCanvas.grid(column=0, row=1)

        self.questionLabel = ttk.Label(self.frm, text="Question!", background="#000fff000")
        self.questionLabel.grid(column=0, row=2)

        self.figureCanvas = FigureCanvasTkAgg(self.fig, self.frm)
        self.figureCanvas.draw()
        self.figureCanvas.get_tk_widget().grid(column=0, row=3)

        self.temp = [0]
        self.temp_time = ['0']

        self.hum = [0]
        self.hum_time = ['0']

        self.audio = 0

        self.avg_temp = [0]
        self.avg_hum = [0]
        self.avg_time = ['0']

        self.question = 0
        self.questionColor = "#eeeeeeeee"

        self.publisher.sub_list['Temperature'].append(self.update_temp)
        self.publisher.sub_list['Humidity'].append(self.update_hum)
        self.publisher.sub_list['Audio'].append(self.update_audio)
        self.publisher.sub_list['Close'].append(self.exit)

    async def run(self):
        self.gui_tasks[0] = asyncio.create_task(self.run_loop(), name='gui_loop')
        self.todo.add(self.gui_tasks[0])

        self.gui_tasks[1] = asyncio.create_task(self.update_avg(), name='avg_graph_loop')
        self.todo.add(self.gui_tasks[1])

    async def run_loop(self):
        self.dataLabel['text'] = f'Temperature: {self.temp[-1]}, Humidity: {self.hum[-1]}, Volume: {self.audio}'

        if self.question:
            self.questionLabel['background'] = '#000fff000'
            self.questionLabel['text'] = 'Question!'
        else:
            self.questionLabel['background'] = '#eeeeeeeee'
            self.questionLabel['text'] = 'No questions'

        self.avg_plot.clear()
        self.avg_plot.plot(self.avg_time, self.avg_temp, color='r', label='Temperature')
        self.avg_plot.plot(self.avg_time, self.avg_hum, color='b', label='Humidity')
        self.avg_plot.set_xlabel('Time [H:M]')
        self.avg_plot.set_ylabel('Magnitude')
        self.avg_plot.title.set_text('Average temperature and humidity')
        self.avg_plot.legend()

        self.questionIndicator = self.questionCanvas.create_oval(0, 0, 10, 10, fill='#000fff000')

        self.figureCanvas.draw()
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

    def update_question(self, msg):
        if re.search("011..010", msg):
            self.question = 1
            color = msg[-3:-1]
            if color == "000":
                #RED
                pass
            elif color == "001":

                pass
            elif color == "010":
                pass
            elif color == "011":
                pass
        elif msg == "01000010":
            self.question = 0

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

    async def exit(self):
        for task in self.gui_tasks:
            task.cancel()
        self.root.destroy()
