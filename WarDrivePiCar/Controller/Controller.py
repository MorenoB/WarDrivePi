from threading import Thread
from time import sleep


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)
