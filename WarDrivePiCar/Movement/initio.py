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
# turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
# turnreverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
# ======================================================================


# Import all necessary libraries
import RPi.GPIO as GPIO

# Pins used to enable/disable the motors & enable/disable forward or backward motion,
IN1 = 18  # Right
IN2 = 23  # Right Backward
IN3 = 24  # Left
IN4 = 25  # Left Backward

# Pins used for PWM, used for motor control
ENA = 17  # Right PWM motor
ENB = 22  # Left PWM motor


# ======================================================================
# General Functions
#
# init(). Initialises GPIO pins, switches motors and LEDs Off, etc
def init():
    global pin_ena, pin_enb

    GPIO.setwarnings(False)

    # use BCM pin numbering
    GPIO.setmode(GPIO.BCM)
    # print GPIO.RPI_REVISION

    # Right motors activation and deactivation
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)

    # Left motors activation and deactivation
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    GPIO.setup(ENA, GPIO.OUT)
    pin_ena = GPIO.PWM(ENA, 20)
    pin_ena.start(0)

    GPIO.setup(ENB, GPIO.OUT)
    pin_enb = GPIO.PWM(ENB, 20)
    pin_enb.start(0)


# cleanup(). Sets all motors off and sets GPIO to standard values
def cleanup():
    stop()
    GPIO.cleanup()


# version(). Returns 1. Invalid until after init() has been called
def version():
    return 1


# End of General Functions
# ======================================================================


# ======================================================================
# Motor Functions
#
# stop(): Stops both motors
def stop():
    pin_ena.ChangeDutyCycle(0)
    pin_enb.ChangeDutyCycle(0)


# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
def forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    pin_ena.ChangeDutyCycle(speed)
    pin_enb.ChangeDutyCycle(speed)

    pin_ena.ChangeFrequency(speed + 5)
    pin_enb.ChangeFrequency(speed + 5)


# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
def reverse(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    pin_ena.ChangeDutyCycle(speed)
    pin_enb.ChangeDutyCycle(speed)

    pin_ena.ChangeFrequency(speed + 5)
    pin_enb.ChangeFrequency(speed + 5)


# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spin_left(speed):

    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

    pin_ena.ChangeDutyCycle(speed)
    pin_enb.ChangeDutyCycle(speed)
    pin_ena.ChangeFrequency(speed + 5)
    pin_enb.ChangeFrequency(speed + 5)


# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spin_right(speed):

    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

    pin_ena.ChangeDutyCycle(speed)
    pin_enb.ChangeDutyCycle(speed)

    pin_ena.ChangeFrequency(speed + 5)
    pin_enb.ChangeFrequency(speed + 5)


# turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
#def turn_forward(left_speed, right_speed):
#    pin_ena.ChangeDutyCycle(left_speed)
#    pin_enb.ChangeDutyCycle(right_speed)
#    pin_ena.ChangeFrequency(left_speed + 5)
#    pin_enb.ChangeFrequency(right_speed + 5)


# turnReverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
#def turn_reverse(left_speed, right_speed):
#    pin_ena.ChangeDutyCycle(left_speed)
#    pin_enb.ChangeDutyCycle(right_speed)
#    pin_ena.ChangeFrequency(left_speed + 5)
#    pin_enb.ChangeFrequency(right_speed + 5)


# End of Motor Functions
# ======================================================================