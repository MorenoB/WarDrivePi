from threading import Thread
from time import sleep
from Movement.initio import Initio
from pubsub import pub

class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __carMovement = None

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        self.__carMovement = Initio()
        self.__carMovement.forward(50)

        # Register events
        pub.subscribe(self.__print_number_of_left_pulses, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__print_number_of_right_pulses, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Main Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

        self.__shutdown_controller()

    def __print_number_of_left_pulses(self, left_pulses):
        print "Left pulses: ", left_pulses

    def __print_number_of_right_pulses(self, right_pulses):
        print "Right pulses: ", right_pulses

    def __shutdown_controller(self):
        print "Shutting down controller..."
        self.__carMovement.cleanup()
