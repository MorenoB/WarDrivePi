from threading import Thread
from time import sleep

from pubsub import pub

from keyboard import Keyboard
from Communication.gps import GPS
from Movement.car_control import CarControl
from Util.enums import MovementType


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 50  # 50% of the motor speed.
    __CM_PER_PULSE = 0.2  # TODO : Need to verify in Real-Life, will need to bring a ruler to the car and check how
    # much cm's is between a hole.

    __carMovement = None

    __isRunning = False
    __moveType = MovementType.Idle

    __cm_driven_right = 0
    __cm_driven_left = 0

    # Coordinates tweaking
    __coordinateSensitivity = 0.0001

    # Current coordinates
    __latitude = 0
    __longitude = 0

    # Target coordinates
    __targetLatitude = 0
    __targetLongitude = 0

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = CarControl()
        self.__carMovement.setup_pins()

        # We will disable pulse updates when in spinning mode for now.
        self.__carMovement.DontPulseUpdateWhenSpinning = True

        # Register car events
        pub.subscribe(self.__on_left_pulse_update, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__on_right_pulse_update, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Register keyboard events
        pub.subscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

        # Register gps events
        pub.subscribe(self.__on_longitude_changed, GPS.EVENT_ON_LONGITUDE_CHANGED)
        pub.subscribe(self.__on_latitude_changed, GPS.EVENT_ON_LATITUDE_CHANGED)

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Controller)

    def run(self):

        self.__isRunning = True

        # Program Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

            if self.__needs_to_move_to_target_coordinates:
                self.__go_to_target_coordinates()

    def __needs_to_move_to_target_coordinates(self):

        if self.__targetLatitude == 0 or self.__targetLongitude == 0:
            return False

        # If our longitude or our latitude is not within a valid range of the target, then we need to move
        if not self.__targetLatitude - self.__coordinateSensitivity <= self.__latitude <= self.__targetLatitude + \
                self.__coordinateSensitivity:
            return True

        if not self.__targetLongitude - self.__coordinateSensitivity <= self.__longitude <= self.__targetLongitude + \
                self.__coordinateSensitivity:
            return True

        return False

    def __go_to_target_coordinates(self):
        difference_latitude = self.__targetLatitude - self.__latitude
        difference_longitude = self.__targetLongitude - self.__longitude

        # If we are out of range on longitude, do something
        if not -self.__coordinateSensitivity <= difference_longitude <= self.__coordinateSensitivity:
            # TODO : Move towards longitude point by moving the car
            return

        # If we are out of range on latitude, do something
        if not -self.__coordinateSensitivity <= difference_latitude <= self.__coordinateSensitivity:
            # TODO : Move towards latitude point by moving the car
            return

        return

    def print_distance_driven(self):
        print "Left cm's driven : " + str(self.__cm_driven_left)
        print "Right cm's driven : " + str(self.__cm_driven_right)
        print "Average distance travelled : ", self.__get_average_distance_driven()

    def __on_longitude_changed(self, longitude):

        if self.__longitude == longitude:
            return

        print "Average longitude is now ", longitude
        self.__longitude = longitude

    def __on_latitude_changed(self, latitude):

        if self.__latitude == latitude:
            return

        print "Average latitude is now ", latitude
        self.__latitude = latitude

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

        pub.unsubscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

        pub.unsubscribe(self.__on_latitude_changed, GPS.EVENT_ON_LATITUDE_CHANGED)
        pub.unsubscribe(self.__on_longitude_changed, GPS.EVENT_ON_LONGITUDE_CHANGED)

        print "Cleaning up GPIO"
        self.__carMovement.cleanup()
        print "Shutting down controller..."
        self.__isRunning = False
