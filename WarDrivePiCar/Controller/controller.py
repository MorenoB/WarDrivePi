from threading import Thread
from time import sleep

from pubsub import pub

from keyboard import Keyboard
from Movement.car_control import CarControl
from Util.enums import MovementType


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 50  # 50% of the motor speed.
    __CM_PER_PULSE = 0.2  # TODO : Need to verify in Real-Life, will need to bring a ruler to the car and check how
    # much cm's is between a hole.

    __carMovement = None
    __isRunning = False

    __lastMoveCommand = "NONE"
    __moveType = MovementType.Idle

    __cm_driven_right = 0
    __cm_driven_left = 0

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = CarControl()
        self.__carMovement.setup_pins()

        # We will disable pulse updates when in spinning mode for now.
        self.__carMovement.DontPulseUpdateWhenSpinning = True

        # Register events
        pub.subscribe(self.__on_left_pulse_update, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__on_right_pulse_update, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Register events
        pub.subscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Controller)

    def run(self):

        self.__isRunning = True

        # Program Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

    def print_distance_driven(self):
        print "Left cm's driven : " + str(self.__cm_driven_left)
        print "Right cm's driven : " + str(self.__cm_driven_right)
        print "Average distance travelled : ", self.__get_average_distance_driven()

    def __on_keyboard_movetype_changed(self, move_type):

        # If we somehow receive a double movetype 'change'
        if self.__moveType == move_type:
            return

        self.__carMovement.IsSpinning = False

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
            self.__carMovement.IsSpinning = True
            self.__carMovement.spin_left(self.__CAR_SPEED)
        elif move_type == MovementType.Spin_Right:
            self.__carMovement.IsSpinning = True
            self.__carMovement.spin_right(self.__CAR_SPEED)

        self.__moveType = move_type

    def __on_left_pulse_update(self, left_pulses):
        self.__cm_driven_left = int(left_pulses) * float(self.__CM_PER_PULSE)

        print "Left pulses: ", left_pulses

        # Will print distance driven for now
        # TODO : Make a better use of this 'Print distance travelled' function call, not on every left pulse update.
        self.print_distance_driven()

    def __on_right_pulse_update(self, right_pulses):
        self.__cm_driven_right = int(right_pulses) * float(self.__CM_PER_PULSE)

        print "Right pulses: ", right_pulses

    def __get_average_distance_driven(self):
        return (self.__cm_driven_left + self.__cm_driven_right) / 2

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        # De-register events
        pub.unsubscribe(self.__on_left_pulse_update, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.unsubscribe(self.__on_right_pulse_update, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        print "Cleaning up GPIO"
        self.__carMovement.cleanup()
        print "Shutting down controller..."
        self.__isRunning = False
