import asyncio
import random
from tinydb import TinyDB, Query
from datetime import datetime

db = None
User = None
prop_id_translation = None
process_func = None
todo = None


def store(prop_id, data):
    print('Processing data...')
    date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    data_type = prop_id_translation[prop_id]
    sensor_data = process_func[data_type](data)
    print('Storing data...')
    db.upsert({'Date': date, data_type: sensor_data}, User.Date == date)
    print(date, ' - ', data_type, ': ', sensor_data)


def divide(data):
    data = float(data)/100
    return data


# simulates waiting for a message with a random wait time of 0, 1, or 2 seconds
async def get_message():
    print('Getting message...')
    wait_time = random.randint(0, 2)
    print('Message wait time: ', wait_time)
    await asyncio.sleep(wait_time)
    # generate a random message within the format
    msg = f'color clock {random.choice(["DATA", "REQ"])}: pubaddr receivedaddr {random.choice(["0x75", "0xa7"])} ' \
          f'{random.randint(0, 100)} END'
    print(msg)
    print('message found!')
    return msg


# identify message type and pass to appropriate function
async def message_handler(msg):
    print('decoding message...')
    parsed_msg = msg.split()
    if parsed_msg[2] == 'DATA:':
        print('data message')
        prop_id = parsed_msg[5]
        data = parsed_msg[6]
        store(prop_id, data)
    elif parsed_msg[2] == 'REQ:':
        # request type not implemented, currently same as data message
        print('request message')
        prop_id = parsed_msg[5]
        data = parsed_msg[6]
        store(prop_id, data)
    else:
        print('message not supported')


async def mainloop():
    global db
    global User
    global prop_id_translation
    global process_func
    global todo

    db = TinyDB('db.json')
    db.truncate()
    User = Query()
    prop_id_translation = {'0x75': 'Temperature', '0xa7': 'Humidity'}
    process_func = {'Temperature': divide, 'Humidity': divide}
    todo = set()

    for i in range(10):
        # wait for a new message
        msg = await get_message()

        # add the message to a list of task to be completed
        task = asyncio.create_task(message_handler(msg), name=f'{i}')
        todo.add(task)
        # check if any tasks have been completed
        pending = asyncio.all_tasks()
        # and remove those tasks from the list
        todo.intersection_update(pending)
        print('Pending tasks: ', len(todo))

    # wait for all tasks to be completed before exiting the program
    while len(todo):
        print('Waiting for all tasks to finish...')
        done, _pending = await asyncio.wait(todo, timeout=1)
        todo.difference_update(done)
        msg_ids = (t.get_name() for t in todo)
        print(f'{len(todo)}: ' + ', '.join(sorted(msg_ids)))


if __name__ == '__main__':
    asyncio.run(mainloop())
