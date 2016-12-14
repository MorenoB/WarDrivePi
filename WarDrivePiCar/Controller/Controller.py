from threading import Thread
from time import sleep
from Movement import initio


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        initio.init()
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

            initio.forward(50)

        self.__shutdown_controller()

    def __shutdown_controller(self):
        print "Shutting down controller..."
        initio.cleanup()
