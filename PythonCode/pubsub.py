import asyncio


class Publisher:
    def __init__(self, todo):
        self.sub_list = {'Temperature': [], 'Humidity': [], 'Audio': [], 'Question': [], 'Close': []}

        self.todo = todo

    def publish(self, topic):
        if topic not in self.sub_list:
            print('Unknown topic')
            return
        for sub in self.sub_list[topic]:
            task = asyncio.create_task(sub(), name=f'{topic}_events')
            self.todo.add(task)
