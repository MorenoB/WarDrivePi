from time import sleep

from Movement.CarControl import CarControl
from pubsub import pub
from threading import Thread
from Keyboard import Keyboard
from WarDrivePiCar.Enums import MovementType


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 50

    __carMovement = None
    __isRunning = False

    __lastMoveCommand = "NONE"

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = CarControl()
        self.__carMovement.setup_pins()

        # Register events
        pub.subscribe(self.__print_number_of_left_pulses, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__print_number_of_right_pulses, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Register events
        pub.subscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Controller)

    def run(self):

        self.__isRunning = True

        # Main Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

    def __on_keyboard_movetype_changed(self, move_type):
        if move_type == MovementType.Forward:
            self.__carMovement.forward(self.__CAR_SPEED)
        elif move_type == MovementType.Reverse:
            self.__carMovement.reverse(self.__CAR_SPEED)
        elif move_type == MovementType.Idle:
            self.__carMovement.stop()
        elif move_type == MovementType.Turn_Left:
            self.__carMovement.turn_left()
        elif move_type == MovementType.Turn_Right:
            self.__carMovement.turn_right()
        elif move_type == MovementType.Spin_Left:
            self.__carMovement.spin_left(self.__CAR_SPEED)
        elif move_type == MovementType.Spin_Right:
            self.__carMovement.spin_right(self.__CAR_SPEED)

        print "Movetype changed to " + str(move_type)

    @staticmethod
    def __print_number_of_left_pulses(left_pulses):
        print "Left pulses: ", left_pulses

    @staticmethod
    def __print_number_of_right_pulses(right_pulses):
        print "Right pulses: ", right_pulses

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        # De-register events
        pub.unsubscribe(self.__print_number_of_left_pulses, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.unsubscribe(self.__print_number_of_right_pulses, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        print "Cleaning up GPIO"
        self.__carMovement.cleanup()
        print "Shutting down controller..."
        self.__isRunning = False
