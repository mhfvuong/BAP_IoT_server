import asyncio
import serial
import random
try:
    import serial_asyncio
    operation_mode = None
except ModuleNotFoundError:
    print('Module serial_asyncio not found, continuing in test mode...')
    operation_mode = False

from GUI import GUI
from database import Database
from pubsub import Publisher
from preprocessing import Preprocessing
from webapp import WebApp


class Server:
    def __init__(self, operation_mode):
        self.loop = True
        self.todo = set()
        self.prop_id_translation = {'0x75': 'Temperature', '0xa7': 'Humidity', '0x79': 'Audio'}

        self.reader = None
        self.writer = None
        self.operation_mode = operation_mode

        self.db = Database()
        self.publisher = Publisher(self.todo)
        self.preprocessing = Preprocessing()
        self.gui = GUI(self.db, self.publisher, self.todo)
        self.webapp = WebApp('webapp', self.db, self.publisher, self.todo)

        self.publisher.sub_list['Close'].append(self.close_server)

    # simulates waiting for a message with a random wait time of 0, 1, or 2 seconds
    async def get_message(self):
        wait_time = random.randint(0, 3)
        print('Message wait time: ', wait_time)
        await asyncio.sleep(wait_time)

        # generate a random message within the format
        msg = f'color clock DATA: pubaddr receivedaddr {random.choice(["0x75", "0xa7", "0x79"])} ' \
              f'{random.randint(100, 3000)} END'
        print(msg)
        return msg

    async def send_message(self):
        self.writer.write(b'message send')

    # identify message type and pass to appropriate function
    async def message_handler(self, msg):
        parsed_msg = msg.split()

        try:
            if parsed_msg[2] == 'DATA:':
                data_type = self.prop_id_translation.get(str(parsed_msg[5]))
                data = self.preprocessing.process_func.get(data_type, lambda x: x)(parsed_msg[6])
                if data is not None:
                    self.db.store(data_type, data)
                    self.publisher.publish(data_type)

            else:
                print('message not supported')

        except IndexError:
            print('message too short')

    async def run(self):
        if self.operation_mode:
            try:
                self.reader, self.writer = await serial_asyncio.open_serial_connection(url='/dev/ttyACM0',
                                                                                       baudrate=115200)
            except serial.SerialException:
                print('No USB connection found, continuing in test mode...')
                self.operation_mode = False

        await self.gui.run()
        await self.webapp.run()
        i = 0

        while self.loop:
            print(self.todo)
            # wait for a new message
            if self.operation_mode:
                msg = await self.reader.readline()
            else:
                msg = await self.get_message()

            # add the message to a list of task to be completed
            self.todo.add(asyncio.create_task(self.message_handler(msg), name=f'{i}'))

            # check if any tasks have been completed
            pending = asyncio.all_tasks()
            # and remove those tasks from the list
            self.todo.intersection_update(pending)
            print('Pending tasks: ', len(self.todo))

            i += 1

        # wait for all tasks to be completed before exiting the program
        while len(self.todo):
            print('Waiting for all tasks to finish...')
            done, _pending = await asyncio.wait(self.todo, timeout=1)
            self.todo.difference_update(done)
            msg_ids = (t.get_name() for t in self.todo)
            print(f'{len(self.todo)}: ' + ', '.join(sorted(msg_ids)))

    async def close_server(self):
        self.loop = False


if __name__ == '__main__':
    while operation_mode is None:
        print('Test or operation mode? t/o')
        toinput = input()
        if toinput == 't':
            operation_mode = False
            print('Continuing in test mode...')
            break
        elif toinput == 'o':
            operation_mode = True
            print('Continuing in operation mode...')
            break
        print('Unrecognized mode')
    server = Server(operation_mode)
    asyncio.run(server.run())
