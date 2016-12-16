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
from axel import Event

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('----------------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO can only be run on the RPi. Falling back to mock objects.')
    print('----------------------------------------------------------------------------')
    import gpio_mock as GPIO
except ImportError:
    print('-------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO library not found. Falling back to mock objects.')
    print('-------------------------------------------------------------------')
    import gpio_mock as GPIO


class Initio():

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
    SPEED_ENCODER_RIGHT_INTERRUPT = 2  # Right interrupt speed encoder value
    SPEED_ENCODER_RIGHT_DIRECTION = 3  # Right direction speed encoder value

    # Values from the wheel speed encoders.
    direction = ""
    numberOfRightPulses = 0
    numberOfLeftPulses = 0

    # init(). Initialises GPIO pins, switches motors and LEDs Off, etc
    def __init__(self):
        # Set up events.
        self.onLeftEncoderTriggered = Event(self)
        self.onRightEncoderTriggered = Event(self)

        GPIO.setwarnings(False)

        # use BCM pin numbering
        GPIO.setmode(GPIO.BCM)
        # print GPIO.RPI_REVISION

        # Right motors activation and deactivation
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)

        # Left motors activation and deactivation
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        GPIO.setup(self.ENA, GPIO.OUT)
        self.pin_ena = GPIO.PWM(self.ENA, 20)
        self.pin_ena.start(0)

        GPIO.setup(self.ENB, GPIO.OUT)
        self.pin_enb = GPIO.PWM(self.ENB, 20)
        self.pin_enb.start(0)

        GPIO.add_event_detect(self.SPEED_ENCODER_LEFT_INTERRUPT, GPIO.FALLING,
                              callback=self.__left_encoder_callback(self), bouncetime=self.__BOUNCE_TIME)
        GPIO.add_event_detect(self.SPEED_ENCODER_RIGHT_INTERRUPT, GPIO.FALLING,
                              callback=self.__right_encoder_callback(self), bouncetime=self.__BOUNCE_TIME)

    def __left_encoder_callback(self, channel):
        if GPIO.input(self.SPEED_ENCODER_LEFT_DIRECTION) == GPIO.HIGH:
            self.numberOfLeftPulses += 1
        else:
            self.numberOfLeftPulses -= 1

        self.direction = "LEFT"
        self.onLeftEncoderTriggered.fire(self, {})

    def __right_encoder_callback(self, channel):
        if GPIO.input(self.SPEED_ENCODER_RIGHT_DIRECTION) == GPIO.HIGH:
            self.numberOfRightPulses += 1
        else:
            self.numberOfRightPulses -= 1

        self.direction = "RIGHT"
        self.onRightEncoderTriggered.fire(self, {})

        # cleanup(). Sets all motors off and sets GPIO to standard values
    def cleanup(self):
        self.stop()
        GPIO.cleanup()

    # version(). Returns 1. Invalid until after init() has been called
    def version(self):
        return 1

    # stop(): Stops both motors
    def stop(self):
        self.pin_ena.ChangeDutyCycle(0)
        self.pin_enb.ChangeDutyCycle(0)

    # forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
    def forward(self, speed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)

        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

    # reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
    def reverse(self, speed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)

        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

    # spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
    def spin_left(self, speed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)

        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

    # spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
    def spin_right(self, speed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)

        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

        self.pin_ena.ChangeDutyCycle(speed)
        self.pin_enb.ChangeDutyCycle(speed)

        self.pin_ena.ChangeFrequency(speed + 5)
        self.pin_enb.ChangeFrequency(speed + 5)

        # turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,
        # rightSpeed <= 100
        # def turn_forward(left_speed, right_speed):
        #    pin_self.ENA.ChangeDutyCycle(left_speed)
        #    pin_self.ENB.ChangeDutyCycle(right_speed)
        #    pin_self.ENA.ChangeFrequency(left_speed + 5)
        #    pin_self.ENB.ChangeFrequency(right_speed + 5)

        # turnReverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0
        # <= leftSpeed,rightSpeed <= 100
        # def turn_reverse(left_speed, right_speed):
        #    pin_self.ENA.ChangeDutyCycle(left_speed)
        #    pin_self.ENB.ChangeDutyCycle(right_speed)
        #    pin_self.ENA.ChangeFrequency(left_speed + 5)
        #    pin_self.ENB.ChangeFrequency(right_speed + 5)
