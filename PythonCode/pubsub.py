import asyncio


class Publisher:
    def __init__(self, todo):
        self.sub_list = {'Temperature': [], 'Humidity': [], 'Close': []}

        self.todo = todo

    def publish(self, topic):
        for sub in self.sub_list[topic]:
            task = asyncio.create_task(sub(), name=f'{topic}_events')
            self.todo.add(task)
