from threading import Thread
from time import sleep

from pubsub import pub

from keyboard import Keyboard
from Communication.phone_handler import Phone
from Communication.internet_connection_checker import InternetConnectionChecker
from Movement.car_control import CarControl
from Util.enums import MovementType, CompassDirections
from Util.extensions import convert_compass_direction_to_angle, convert_int_to_degrees


class Controller(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 15  # 15% of the motor speed.
    __CM_PER_PULSE = 0.2  # TODO : Need to verify in Real-Life, will need to bring a ruler to the car and check how
    # much cm's is between a hole.

    __carMovement = None

    __isRunning = False
    __moveType = MovementType.Idle

    __cm_driven_right = 0
    __cm_driven_left = 0

    # Coordinates tweaking
    __coordinateMargin = 0.0001

    # Current coordinates
    __latitude = 0
    __longitude = 0
    __altitude = 0
    __accuracy = 0

    # Target coordinates
    __targetLatitude = 0
    __targetLongitude = 0

    # Compass variables
    __angleInDegrees = -999
    __compassDirection = None
    __angleMargin = 20
    __targetAngle = convert_compass_direction_to_angle(CompassDirections.North)

    # Public bools
    EnableGPSWaypointSystem = True

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = CarControl()
        self.__carMovement.setup_pins()

        # We will disable pulse updates when in spinning mode for now.
        self.__carMovement.DontPulseUpdateWhenGoingLeftOrRight = True

        # Register car events
        pub.subscribe(self.__on_left_pulse_update, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.subscribe(self.__on_right_pulse_update, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        # Register keyboard events
        pub.subscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

        # Register phone events
        pub.subscribe(self.__on_location_changed, Phone.EVENT_ON_LOCATION_CHANGED)
        pub.subscribe(self.__on_compass_changed, Phone.EVENT_ON_COMPASS_CHANGED)

        # Register internet connection checker events
        pub.subscribe(self.__on_internet_connection_changed, InternetConnectionChecker.EVENT_ON_INTERNET_CONNECTION_CHANGED)

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Controller)

    def run(self):

        self.__isRunning = True

        # Program Loop
        while not self.name.endswith("--"):
            sleep(self.__CPU_CYCLE_TIME)

            # If we have enabled the GPS way-point system, go to target angle if we get compass update.
            if self.EnableGPSWaypointSystem:
                if self.__needs_to_move_to_target_coordinates:
                    self.__calculate_target_angle()

                    if self.__is_in_target_angle():
                        # TODO : Move towards point by moving the car forward when in correct direction
                        self.__carMovement.forward(1)
                    else:
                        self.__go_to_target_angle()
                        continue
                # Reached coordinate, stop!
                self.__carMovement.stop()

    def __needs_to_move_to_target_coordinates(self):

        if self.__targetLatitude == 0 or self.__targetLongitude == 0:
            return False

        difference_latitude = abs(self.__targetLatitude - self.__latitude)
        difference_longitude = abs(self.__targetLongitude - self.__longitude)

        # If our longitude or our latitude is not within a valid range of the target, then we need to move
        if not difference_longitude < self.__coordinateMargin:
            return True

        if not difference_latitude < self.__coordinateMargin:
            return True

        return False

    def __is_in_target_angle(self):

        # Haven't got target angle
        if self.__angleInDegrees == -999:
            return True

        diff_angle = self.__targetAngle - self.__angleInDegrees
        diff_angle = abs(diff_angle)

        # If our current angle is within a valid range of the target angle, return True
        if diff_angle < self.__angleMargin:
            return True

        return False

    def __go_to_target_angle(self):

        target_difference = convert_int_to_degrees(self.__targetAngle - self.__angleInDegrees)

        if target_difference < 180:
            self.__carMovement.spin_right(self.__CAR_SPEED)
        else:
            self.__carMovement.spin_left(self.__CAR_SPEED)

        print "{0} -> Car will rotate to {1} while its own angle is {2}"\
            .format(self.name, self.__targetAngle, self.__angleInDegrees)

    def __calculate_target_angle(self):
        difference_latitude = abs(self.__targetLatitude - self.__latitude)
        difference_longitude = abs(self.__targetLongitude - self.__longitude)

        # If we are out of range on longitude, do something
        if not difference_longitude < self.__coordinateMargin:
            if difference_longitude > 0:
                self.__targetAngle = convert_compass_direction_to_angle(CompassDirections.North)
            elif difference_longitude < 0:
                self.__targetAngle = convert_compass_direction_to_angle(CompassDirections.South)

        # If we are out of range on latitude, do something
        elif not difference_latitude < self.__coordinateMargin:
            if difference_latitude > 0:
                self.__targetAngle = convert_compass_direction_to_angle(CompassDirections.East)
            elif difference_latitude < 0:
                self.__targetAngle = convert_compass_direction_to_angle(CompassDirections.West)

    def print_distance_driven(self):
        print "{0} -> Car average distance travelled = {1}".format(self.name, self.__get_average_distance_driven())

    def __on_compass_changed(self, compass):

        if compass == self.__angleInDegrees:
            return

        self.__angleInDegrees = compass

    def __on_location_changed(self, longitude, latitude, altitude, accuracy):
        self.__longitude = longitude
        self.__latitude = latitude
        self.__altitude = altitude
        self.__accuracy = accuracy

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

        # Will print distance driven for now
        # TODO : Make a better use of this 'Print distance travelled' function call, not on every left pulse update.
        self.print_distance_driven()

    def __on_right_pulse_update(self, right_pulses):
        self.__cm_driven_right = int(right_pulses) * float(self.__CM_PER_PULSE)

    def __get_average_distance_driven(self):
        return (self.__cm_driven_left + self.__cm_driven_right) / 2

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        # De-register events
        pub.unsubscribe(self.__on_left_pulse_update, self.__carMovement.EVENT_ON_LEFT_ENCODER)
        pub.unsubscribe(self.__on_right_pulse_update, self.__carMovement.EVENT_ON_RIGHT_ENCODER)

        pub.unsubscribe(self.__on_keyboard_movetype_changed, Keyboard.EVENT_ON_MOVETYPE_CHANGED)

        pub.unsubscribe(self.__on_location_changed, Phone.EVENT_ON_LOCATION_CHANGED)
        pub.unsubscribe(self.__on_compass_changed, Phone.EVENT_ON_COMPASS_CHANGED)

        self.__carMovement.cleanup()

        print "{0} -> Car controller will shut down...".format(self.name)
        self.__isRunning = False

    def __on_internet_connection_changed(self, has_internet_connection):
        if not has_internet_connection:
            self.__carMovement.stop()
            print "{0} -> Car has lost internet connection!".format(self.name)
