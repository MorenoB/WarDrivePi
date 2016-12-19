from threading import Thread
from time import sleep
from Movement.initio import Initio
from pubsub import pub
from pynput.keyboard import Key, Listener


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __carMovement = None
    __carSpeed = 15

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = Initio()

        # Register events
        pub.subscribe(self.__print_number_of_left_pulses, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__print_number_of_right_pulses, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Collect events until released
        with Listener(
                on_press=self.__on_press,
                on_release=self.__on_release) as listener:
            listener.join()

    def __on_press(self, key):

        # Move the car according to directional keyboard input events
        if key == Key.up:
            self.__carMovement.forward(self.__carSpeed)

        if key == Key.down:
            self.__carMovement.reverse(self.__carSpeed)

        if key == Key.left:
            self.__carMovement.spin_left(self.__carSpeed)

        if key == Key.right:
            self.__carMovement.spin_right(self.__carSpeed)

    def __on_release(self, key):

        # Car needs to stop moving when a key is being released.
        if key == Key.up or key == Key.down or key == Key.left or key == Key.right:
            self.__carMovement.stop()

    def run(self):

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

        # Stop keyboard listener.
        Listener.stop()
