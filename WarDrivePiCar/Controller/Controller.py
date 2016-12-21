from time import sleep

from Movement.initio import Initio
from pubsub import pub
from pynput.keyboard import Key, Listener
from threading import Thread


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __carMovement = None
    __carSpeed = 15
    __rotationSpeed = 5  # This value will be added on top of the __carSpeed value
    __programInstance = None
    __ListenerInstance = None
    __isRunning = False

    def __init__(self, main_obj):
        Thread.__init__(self)

        self.__programInstance = main_obj

        # Initialise car hardware library.
        self.__carMovement = Initio()

        # Register events
        pub.subscribe(self.__print_number_of_left_pulses, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__print_number_of_right_pulses, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

    def __on_press(self, key):

        # Move the car according to directional keyboard input events
        if key == 'W':
            self.__carMovement.forward(self.__carSpeed)

        if key == 'S':
            self.__carMovement.reverse(self.__carSpeed)

        if key == 'A':
            self.__carMovement.turn_forward(self.__carSpeed + self.__rotationSpeed, self.__carSpeed)

        if key == 'D':
            self.__carMovement.turn_forward(self.__carSpeed, self.__carSpeed + self.__rotationSpeed)

        if key == 'Q':
            self.__carMovement.spin_left(self.__carSpeed)

        if key == 'E':
            self.__carMovement.spin_right(self.__carSpeed)

    def __on_release(self, key):

        # Car needs to stop moving when a key is being released.
        if key == 'W' or key == 'S' or key == 'A' or key == 'D' or key == 'Q' or key == 'E':
            self.__carMovement.stop()

        if key == Key.esc:
            print "Stop keyboard command is pressed."
            self.__programInstance.stop()
            print "Shutting down keyboard listener..."
            return False

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Controller)

    def __start_keyboard_listener(self):
        self.__ListenerInstance = Listener(on_press=self.__on_press, on_release=self.__on_release)
        self.__ListenerInstance.name = "Keyboard-Listener"
        self.__ListenerInstance.start()
        self.__ListenerInstance.join()

    def run(self):

        self.__isRunning = True
        # Collect events until released
        self.__start_keyboard_listener()

        # Main Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

    @staticmethod
    def __print_number_of_left_pulses(left_pulses):
        print "Left pulses: ", left_pulses

    @staticmethod
    def __print_number_of_right_pulses(right_pulses):
        print "Right pulses: ", right_pulses

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        print "Cleaning up GPIO"
        self.__carMovement.cleanup()
        print "Shutting down controller..."

        self.__isRunning = False
        # Force the key listener to stop by raising stop exception. This is to prevent thread deadlock.
        try:
            raise self.__ListenerInstance.StopException
        except Listener.StopException:
            pass
