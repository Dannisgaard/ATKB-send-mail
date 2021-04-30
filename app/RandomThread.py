import threading
from random import random

thread = threading.Thread()
thread_stop_event = threading.Event()


class RandomThread(threading.Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        # infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            number = round(random() * 10, 3)
            print(number)
            socketio.emit("newnumber", {"number": number}, namespace="/test")
            sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()
