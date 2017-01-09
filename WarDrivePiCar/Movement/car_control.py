# ======================================================================
# General Functions
#
# init(). Initialises GPIO pins, switches motors off, etc
# cleanup(). Sets all motors off and sets GPIO to standard values
# version(). Returns 1. Invalid until after init() has been called
# ======================================================================


# ======================================================================
# Motor Functions
#
# stop(): Stops both motors
# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
# turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds.
#  0 <= leftSpeed,rightSpeed <= 100
# turnreverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds.
#  0 <= leftSpeed,rightSpeed <= 100
# ======================================================================


# ======================================================================
# Sensor Functions
#
#
# ======================================================================

# Import GPIO library and support mock-up fallback
from pubsub import pub

try:
    import RPi.GPIO as gpio
except RuntimeError:
    print('----------------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO can only be run on the RPi. Falling back to mock objects.')
    print('----------------------------------------------------------------------------')
    import gpio_mock as gpio
except ImportError:
    print('-------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO library not found. Falling back to mock objects.')
    print('-------------------------------------------------------------------')
    import gpio_mock as gpio


class CarControl:

    __BOUNCE_TIME = 200

    # Using BCM pins!
    # Pins used to self.ENAble/disable the motors & self.ENAble/disable forward or backward motion,
    IN1 = 18  # Right
    IN2 = 23  # Right Backward
    IN3 = 24  # Left
    IN4 = 25  # Left Backward

    # Pins used for PWM, used for motor control
    ENA = 17  # Right PWM motor
    ENB = 22  # Left PWM motor

    # Pins used for wheel speed encoders.
    SPEED_ENCODER_LEFT_INTERRUPT = 9  # Left interrupt speed encoder value
    SPEED_ENCODER_LEFT_DIRECTION = 11  # Left direction speed encoder value
    SPEED_ENCODER_RIGHT_INTERRUPT = 5  # Right interrupt speed encoder value
    SPEED_ENCODER_RIGHT_DIRECTION = 6  # Right direction speed encoder value

    # Values from the wheel speed encoders.
    __lastPulseTickDirection = ""
    __numberOfRightPulses = 0
    __numberOfLeftPulses = 0

    # Event identifiers used for event listeners.
    EVENT_ON_LEFT_ENCODER = "OnLeftEncoderTriggered"
    EVENT_ON_RIGHT_ENCODER = "OnRightEncoderTriggered"

    # Wheel speed when turning the car.
    __ROTATING_WHEELS_SPEED = 100
    __COUNTER_ROTATING_WHEELS_SPEED = 5

    __lastWheelEncoderPinUsed = -1
    __currentOperation = "NONE"

    # Housekeeping variables
    IsSpinning = False

    # User configurable variables.
    DontPulseUpdateWhenSpinning = False

    # init(). Initialises GPIO pins, switches motors and LEDs Off, etc
    def __init__(self):
        return

    def setup_pins(self):
        gpio.setwarnings(False)

        # use BCM pin numbering
        gpio.setmode(gpio.BCM)
        # print GPIO.RPI_REVISION

        # Right motors activation and deactivation
        gpio.setup(self.IN1, gpio.OUT)
        gpio.setup(self.IN2, gpio.OUT)

        # Left motors activation and deactivation
        gpio.setup(self.IN3, gpio.OUT)
        gpio.setup(self.IN4, gpio.OUT)

        gpio.setup(self.ENA, gpio.OUT)
        self.pin_ena = gpio.PWM(self.ENA, 20)
        self.pin_ena.start(0)

        gpio.setup(self.ENB, gpio.OUT)
        self.pin_enb = gpio.PWM(self.ENB, 20)
        self.pin_enb.start(0)

        gpio.setup(self.SPEED_ENCODER_LEFT_INTERRUPT, gpio.IN)
        gpio.setup(self.SPEED_ENCODER_RIGHT_INTERRUPT, gpio.IN)

        gpio.setup(self.SPEED_ENCODER_RIGHT_DIRECTION, gpio.IN)
        gpio.setup(self.SPEED_ENCODER_LEFT_DIRECTION, gpio.IN)

        gpio.add_event_detect(self.SPEED_ENCODER_LEFT_INTERRUPT, gpio.FALLING,
                              self.__left_encoder_callback)
        gpio.add_event_detect(self.SPEED_ENCODER_RIGHT_INTERRUPT, gpio.FALLING,
                              self.__right_encoder_callback)

    # cleanup(). Sets all motors off and sets GPIO to standard values
    def cleanup(self):

        if self.__currentOperation == "CLEANUP":
            return

        self.stop()
        gpio.cleanup()
        self.__currentOperation = "CLEANUP"

    def get_current_operation(self):
        return self.__currentOperation

    # stop(): Stops both motors
    def stop(self):

        if self.__currentOperation == "STOP":
            return

        self.pin_ena.ChangeDutyCycle(0)
        self.pin_enb.ChangeDutyCycle(0)
        self.__currentOperation = "STOP"

    # forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
    def forward(self, speed):

        if self.__currentOperation == "FORWARD " + str(speed):
            return

        self.__set_pins_to_forward_mode()

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

        self.__currentOperation = "FORWARD " + str(speed)

    # reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
    def reverse(self, speed):

        if self.__currentOperation == "REVERSE " + str(speed):
            return

        self.__set_pins_to_reverse_mode()

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

        self.__currentOperation = "REVERSE " + str(speed)

    # spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
    def spin_left(self, speed):

        if self.__currentOperation == "SPINLEFT " + str(speed):
            return

        gpio.output(self.IN1, gpio.LOW)
        gpio.output(self.IN2, gpio.HIGH)

        gpio.output(self.IN3, gpio.HIGH)
        gpio.output(self.IN4, gpio.LOW)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

        self.__currentOperation = "SPINLEFT " + str(speed)

    # spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
    def spin_right(self, speed):

        if self.__currentOperation == "SPINRIGHT " + str(speed):
            return

        gpio.output(self.IN1, gpio.HIGH)
        gpio.output(self.IN2, gpio.LOW)

        gpio.output(self.IN3, gpio.LOW)
        gpio.output(self.IN4, gpio.HIGH)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

        self.__currentOperation = "SPINRIGHT " + str(speed)

    def turn_left(self, reverse=False):

        if self.__currentOperation == "TURNLEFT " + str(reverse):
            return

        if reverse:
            self.__turn_reverse(self.__ROTATING_WHEELS_SPEED, self.__COUNTER_ROTATING_WHEELS_SPEED)
        else:
            self.__turn_forward(self.__ROTATING_WHEELS_SPEED, self.__COUNTER_ROTATING_WHEELS_SPEED)

        self.__currentOperation = "TURNLEFT " + str(reverse)

    def turn_right(self, reverse=False):

        if self.__currentOperation == "TURNRIGHT " + str(reverse):
            return

        if reverse:
            self.__turn_reverse(self.__COUNTER_ROTATING_WHEELS_SPEED, self.__ROTATING_WHEELS_SPEED)
        else:
            self.__turn_forward(self.__COUNTER_ROTATING_WHEELS_SPEED, self.__ROTATING_WHEELS_SPEED)

        self.__currentOperation = "TURNRIGHT " + str(reverse)

    # turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,
    # rightSpeed <= 100
    def __turn_forward(self, left_speed, right_speed):
        self.__set_pins_to_forward_mode()

        self.pin_ena.ChangeDutyCycle(left_speed)
        self.pin_enb.ChangeDutyCycle(right_speed)
        self.pin_ena.ChangeFrequency(left_speed + 5)
        self.pin_enb.ChangeFrequency(right_speed + 5)

    # turnReverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0
    # <= leftSpeed,rightSpeed <= 100
    def __turn_reverse(self, left_speed, right_speed):
        self.__set_pins_to_reverse_mode()

        self.pin_ena.ChangeDutyCycle(left_speed)
        self.pin_enb.ChangeDutyCycle(right_speed)
        self.pin_ena.ChangeFrequency(left_speed + 5)
        self.pin_enb.ChangeFrequency(right_speed + 5)

    def __set_pins_to_forward_mode(self):
        gpio.output(self.IN1, gpio.HIGH)
        gpio.output(self.IN2, gpio.LOW)

        gpio.output(self.IN3, gpio.HIGH)
        gpio.output(self.IN4, gpio.LOW)

    def __set_pins_to_reverse_mode(self):
        gpio.output(self.IN1, gpio.LOW)
        gpio.output(self.IN2, gpio.HIGH)

        gpio.output(self.IN3, gpio.LOW)
        gpio.output(self.IN4, gpio.HIGH)

    def __left_encoder_callback(self, channel):

        # Channel is not used but is being given by the GPIO library
        self.__lastWheelEncoderPinUsed = channel

        if self.DontPulseUpdateWhenSpinning and self.IsSpinning:
            return

        if gpio.input(self.SPEED_ENCODER_LEFT_DIRECTION) == gpio.HIGH:
            self.__numberOfLeftPulses += 1
        else:
            self.__numberOfLeftPulses -= 1

        self.__lastPulseTickDirection = "LEFT"
        pub.sendMessage(self.EVENT_ON_LEFT_ENCODER, left_pulses=self.__numberOfLeftPulses)

    def __right_encoder_callback(self, channel):

        # Channel is not used but is being given by the GPIO library
        self.__lastWheelEncoderPinUsed = channel

        if self.DontPulseUpdateWhenSpinning and self.IsSpinning:
            return

        if gpio.input(self.SPEED_ENCODER_RIGHT_DIRECTION) == gpio.HIGH:
            self.__numberOfRightPulses += 1
        else:
            self.__numberOfRightPulses -= 1

        self.__lastPulseTickDirection = "RIGHT"
        pub.sendMessage(self.EVENT_ON_RIGHT_ENCODER, right_pulses=self.__numberOfRightPulses)