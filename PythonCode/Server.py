import asyncio
#import serial_asyncio
import random

from GUI import GUI
from database import Database
from pubsub import Publisher
from preprocessing import Preprocessing


class Server:
    def __init__(self):
        self.loop = True
        self.todo = set()
        self.prop_id_translation = {'0x75': 'Temperature', '0xa7': 'Humidity'}

        #self.reader, self.writer = await serial_asyncio.open_serial_connection(url='/dev/ttyACM0', baudrate=115200)

        self.db = Database()
        self.publisher = Publisher(self.todo)
        self.preprocessing = Preprocessing()
        self.gui = GUI(self.db, self.publisher, self.todo)

        self.publisher.sub_list['Close'].append(self.close_server)

    # simulates waiting for a message with a random wait time of 0, 1, or 2 seconds
    async def get_message(self):
        wait_time = random.randint(0, 3)
        print('Message wait time: ', wait_time)
        await asyncio.sleep(wait_time)

        # generate a random message within the format
        msg = f'color clock {random.choice(["DATA", "REQ"])}: pubaddr receivedaddr {random.choice(["0x75", "0xa7"])} ' \
              f'{random.randint(100, 3000)} END'
        print(msg)
        return msg

    # identify message type and pass to appropriate function
    async def message_handler(self, msg):
        parsed_msg = msg.split()

        try:
            if parsed_msg[2] == 'DATA:':
                data_type = self.prop_id_translation[str(parsed_msg[5])]
                data = self.preprocessing.process_func[data_type](parsed_msg[6])
                self.db.store(data_type, data)
                self.publisher.publish(data_type)

            elif parsed_msg[2] == 'REQ:':
                # request type not implemented, currently same as data message
                data_type = self.prop_id_translation[str(parsed_msg[5])]
                data = self.preprocessing.process_func[data_type](parsed_msg[6])
                self.db.store(data_type, data)
                self.publisher.publish(data_type)

            else:
                print('message not supported')

        except IndexError:
            print('message too short')

    async def run(self):
        await self.gui.run(self.loop)
        i = 0

        while self.loop:
            print(self.todo)
            # wait for a new message
            #msg = await self.reader.readline()
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
    server = Server()
    asyncio.run(server.run())
