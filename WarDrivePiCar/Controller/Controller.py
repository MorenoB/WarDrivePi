from threading import Thread
from time import sleep
from Movement.initio import Initio


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __carMovement = None

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        self.__carMovement = Initio()
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

            self.__carMovement.forward(50)

        self.__shutdown_controller()

    def __shutdown_controller(self):
        print "Shutting down controller..."
        self.__carMovement.cleanup()
