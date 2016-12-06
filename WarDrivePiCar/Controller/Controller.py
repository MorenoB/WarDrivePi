from threading import Thread
from time import sleep


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __running = False

    def __init__(self):
        Thread.__init__(self)
        self.startupText = "Hello!"

    def run(self):
        self.__running = True

        while self.__running:
            sleep(self.__CPU_CYCLE_TIME)

    def _stop(self):
        self.__running = False
