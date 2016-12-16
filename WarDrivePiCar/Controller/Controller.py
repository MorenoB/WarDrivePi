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
        self.__carMovement.forward(50)

        # Register events
        self.__carMovement.onRightEncoderTriggered += self.__print_number_of_pulses
        self.__carMovement.onLeftEncoderTriggered += self.__print_number_of_pulses

        # Main Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

        self.__shutdown_controller()

        #  De register events
        self.__carMovement.onRightEncoderTriggered -= self.__print_number_of_pulses
        self.__carMovement.onLeftEncoderTriggered -= self.__print_number_of_pulses

    def __print_number_of_pulses(self):
        print "Left pulses: ", self.__carMovement.numberOfLeftPulses,\
            " Right Pulses: ", self.__carMovement.numberOfRightPulses

    def __shutdown_controller(self):
        print "Shutting down controller..."
        self.__carMovement.cleanup()
