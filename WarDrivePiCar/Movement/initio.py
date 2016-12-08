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


# ======================================================================
# IR Sensor Functions
#
# irLeft(): Returns state of Left IR Obstacle sensor
# irRight(): Returns state of Right IR Obstacle sensor
# irAll(): Returns true if either of the Obstacle sensors are triggered
# irLeftLine(): Returns state of Left IR Line sensor
# irRightLine(): Returns state of Right IR Line sensor
# ======================================================================


# ======================================================================
# UltraSonic Functions
#
# getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
# ======================================================================

# ======================================================================
# Servo Functions
# 
# startServos(). Initialises the servo background process
# stop Servos(). terminates the servo background process
# setServo(Servo, Degrees). Sets the servo to position in degrees -90 to +90
# ======================================================================


# Import all necessary libraries
import RPi.GPIO as GPIO, sys, threading, time, os, subprocess

# Pins used to enable/disable the motors & enable/disable forward or backward motion,
IN1 = 18  # Right
IN2 = 23  # Right Backward
IN3 = 24  # Left
IN4 = 25  # Left Backward

# Pins used for PWM, used for motor control
ENA = 17  # Right PWM motor
ENB = 22  # Left PWM motor



# Define obstacle sensors and line sensors
irFL = 7
irFR = 11
lineRight = 13
lineLeft = 12

# Define Sonar Pin (same pin for both Ping and Echo)
# Note that this can be either 8 or 23 on PiRoCon
sonar = 8

ServosActive = False


# ======================================================================
# General Functions
#
# init(). Initialises GPIO pins, switches motors and LEDs Off, etc
def init():
    global pin_ena, pin_enb

    GPIO.setwarnings(False)

    # use physical pin numbering
    GPIO.setmode(GPIO.BOARD)
    # print GPIO.RPI_REVISION

    # set up digital line detectors as inputs
    GPIO.setup(lineRight, GPIO.IN)  # Right line sensor
    GPIO.setup(lineLeft, GPIO.IN)  # Left line sensor

    # Set up IR obstacle sensors as inputs
    GPIO.setup(irFL, GPIO.IN)  # Left obstacle sensor
    GPIO.setup(irFR, GPIO.IN)  # Right obstacle sensor

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

    start_servos()


# cleanup(). Sets all motors off and sets GPIO to standard values
def cleanup():
    stop()
    stop_servos()
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


# ======================================================================
# IR Sensor Functions
#
# irLeft(): Returns state of Left IR Obstacle sensor
def ir_left():
    if GPIO.input(irFL) == 0:
        return True
    else:
        return False


# irRight(): Returns state of Right IR Obstacle sensor
def ir_right():
    if GPIO.input(irFR) == 0:
        return True
    else:
        return False


# irAll(): Returns true if any of the Obstacle sensors are triggered
def ir_all():
    if GPIO.input(irFL) == 0 or GPIO.input(irFR) == 0:
        return True
    else:
        return False


# irLeftLine(): Returns state of Left IR Line sensor
def ir_left_line():
    if GPIO.input(lineLeft) == 0:
        return True
    else:
        return False


# irRightLine(): Returns state of Right IR Line sensor
def ir_right_line():
    if GPIO.input(lineRight) == 0:
        return True
    else:
        return False


# End of IR Sensor Functions
# ======================================================================


# ======================================================================
# UltraSonic Functions
#
# getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
def get_distance():
    GPIO.setup(sonar, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(sonar, True)
    time.sleep(0.00001)
    GPIO.output(sonar, False)
    start_time = time.time()
    count = time.time()
    GPIO.setup(sonar, GPIO.IN)
    while GPIO.input(sonar) == 0 and time.time() - count < 0.1:
        start_time = time.time()
    count = time.time()
    stop_time = count
    while GPIO.input(sonar) == 1 and time.time() - count < 0.1:
        stop_time = time.time()
    # Calculate pulse length
    elapsed = stop_time - start_time
    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000
    # That was the distance there and back so halve the value
    distance /= 2
    return distance


# End of UltraSonic Functions
# ======================================================================

# ======================================================================
# Servo Functions
# Pirocon/microcon use ServoD to control servos

def set_servo(servo, degrees):
    global ServosActive
    # print "ServosActive:", ServosActive
    # print "Setting servo"
    if not ServosActive:
        start_servos()
    pin_servod(servo, degrees)  # for now, simply pass on the input values


def stop_servos():
    # print "Stopping servo"
    stop_servod()


def start_servos():
    # print "Starting servod as CPU =", CPU
    start_servod()


def start_servod():
    global ServosActive
    # print "Starting servod. ServosActive:", ServosActive
    script_path = os.path.split(os.path.realpath(__file__))[0]
    # os.system("sudo pkill -f servod")
    init_string = "sudo " + script_path + '/servod --pcm --idle-timeout=20000 --p1pins="18,22" > /dev/null'
    os.system(init_string)
    # print init_string
    ServosActive = True


def pin_servod(pin, degrees):
    # print pin, degrees
    pin_string = "echo " + str(pin) + "=" + str(50 + ((90 - degrees) * 200 / 180)) + " > /dev/servoblaster"
    # print pin_string
    os.system(pin_string)


def stop_servod():
    global ServosActive
    os.system("sudo pkill -f servod")
    ServosActive = False
