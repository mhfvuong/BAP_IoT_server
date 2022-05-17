import asyncio
import random
from datetime import datetime
import globals

from request_data import get_most_recent

from tkinter import *
from tkinter import ttk

loop = True
sub_list = {'Temperature': [], 'Humidity': []}


class GUI:
    def __init__(self):
        # initialize GUI
        self.root = Tk()
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        ttk.Label(self.frm, text='Temperature: ..., Humidity: ...').grid(column=0, row=0)
        ttk.Button(self.frm, text='Exit', command=self.exit_gui).grid(column=0, row=1)

        self.temp = 0
        self.hum = 0

        global sub_list
        sub_list['Temperature'].append(self.update_temp)
        sub_list['Humidity'].append(self.update_hum)
        pass

    async def gui_loop(self):
        global loop
        ttk.Label(self.frm, text=f'Temperature: {self.temp}, Humidity: {self.hum}').grid(column=0, row=0)
        self.root.update()
        await asyncio.sleep(0.1)
        if loop:
            asyncio.create_task(self.gui_loop(), name='gui_loop')

    async def update_temp(self):
        self.temp = get_most_recent('Temperature')

    async def update_hum(self):
        self.hum = get_most_recent('Humidity')

    def exit_gui(self):
        global loop
        loop = False
        self.root.destroy()


def publish(topic):
    global sub_list
    for sub in sub_list[topic]:
        asyncio.create_task(sub(), name=f'{topic}_events')


def store(prop_id, data):
    date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    data_type = globals.prop_id_translation[prop_id]
    sensor_data = globals.process_func[data_type](data)
    globals.db.upsert({'Date': date, data_type: sensor_data}, globals.User.Date == date)
    publish(data_type)
    print(date, ' - ', data_type, ': ', sensor_data)


# simulates waiting for a message with a random wait time of 0, 1, or 2 seconds
async def get_message():
    wait_time = random.randint(0, 2)
    print('Message wait time: ', wait_time)
    await asyncio.sleep(wait_time)
    # generate a random message within the format
    msg = f'color clock {random.choice(["DATA", "REQ"])}: pubaddr receivedaddr {random.choice(["0x75", "0xa7"])} ' \
          f'{random.randint(0, 100)} END'
    print(msg)
    return msg


# identify message type and pass to appropriate function
async def message_handler(msg):
    parsed_msg = msg.split()
    try:
        if parsed_msg[2] == b'DATA:' or parsed_msg[2] == 'DATA:':
            prop_id = parsed_msg[5]
            data = parsed_msg[6]
            store(prop_id, data)
            
        elif parsed_msg[2] == b'REQ:' or parsed_msg[2] == 'REQ:':
            # request type not implemented, currently same as data message
            prop_id = parsed_msg[5]
            data = parsed_msg[6]
            store(prop_id, data)
        else:
            print('message not supported')
    except IndexError:
        print('message too short')


async def mainloop():
    global loop

    i = 0
    gui = GUI()
    asyncio.create_task(gui.gui_loop(), name='gui_loop')

    while loop:
        # wait for a new message
        msg = await get_message()

        # add the message to a list of task to be completed
        task = asyncio.create_task(message_handler(msg), name=f'{i}')
        globals.todo.add(task)
        # check if any tasks have been completed
        pending = asyncio.all_tasks()
        # and remove those tasks from the list
        globals.todo.intersection_update(pending)
        print('Pending tasks: ', len(globals.todo))
        i += 1

    # wait for all tasks to be completed before exiting the program
    while len(globals.todo):
        print('Waiting for all tasks to finish...')
        done, _pending = await asyncio.wait(globals.todo, timeout=1)
        globals.todo.difference_update(done)
        msg_ids = (t.get_name() for t in globals.todo)
        print(f'{len(globals.todo)}: ' + ', '.join(sorted(msg_ids)))


if __name__ == '__main__':
    globals.init()
    asyncio.run(mainloop())
