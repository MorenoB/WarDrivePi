from Movement.CarControl import CarControl
from pynput.keyboard import Key, Listener
from threading import Thread


class Keyboard(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 50

    __carMovement = None
    __isRunning = False
    __programInstance = None

    __lastMoveCommand = "NONE"

    def __init__(self, program_instance):
        Thread.__init__(self)

        self.__programInstance = program_instance
        # Initialise car hardware library.
        self.__carMovement = CarControl()

    def __on_press(self, key):

        # Move the car according to directional keyboard input events
        if key == Key.up:
            self.__carMovement.forward(self.__CAR_SPEED)
            self.__lastMoveCommand = "FORWARD"

        if key == Key.down:
            self.__carMovement.reverse(self.__CAR_SPEED)
            self.__lastMoveCommand = "REVERSE"

        if key == Key.left:
            self.__carMovement.turn_left()
            self.__lastMoveCommand = "TURNLEFT"

        if key == Key.right:
            self.__carMovement.turn_right()
            self.__lastMoveCommand = "TURNRIGHT"

        if key == Key.page_up:
            self.__carMovement.spin_left(self.__CAR_SPEED)
            self.__lastMoveCommand = "SPINLEFT"

        if key == Key.page_down:
            self.__carMovement.spin_right(self.__CAR_SPEED)
            self.__lastMoveCommand = "SPINRIGHT"

    def __on_release(self, key):

        # Car needs to stop moving when a key is being released.
        if key == Key.up or key == Key.down or key == Key.left or key == Key.right or key == Key.page_up \
                or key == Key.page_down:
            self.__carMovement.stop()
            self.__lastMoveCommand = "STOP"

        if key == Key.esc:
            print "Shutdown keyboard press received! Calling stop()..."
            self.__programInstance.stop()
            return False

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Keyboard)

    def __start_keyboard_listener(self):
        with Listener(
                on_press=self.__on_press, on_release=self.__on_release)\
                as listener:
            listener.join()
            listener.name = "Keyboard-Listener"

    def run(self):

        self.__isRunning = True
        # Collect events until released
        self.__start_keyboard_listener()

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        self.__isRunning = False
        print "Shutting down keyboard controller..."
        try:
            raise Listener.StopException
        except Listener.StopException:
            pass
