# Import all necessary libraries
from gpiocrust import Header, OutputPin, PWMOutputPin

# Board setup is being used.
# Pins used to enable/disable the motors & enable/disable forward or backward motion,
IN1 = 12  # Right
IN2 = 16  # Right Backward
IN3 = 18  # Left
IN4 = 22  # Left Backward

# Pins used for PWM, used for motor control
ENA = 11  # Right PWM motor
ENB = 15  # Left PWM motor


# stop(): Stops both motors
def stop():

    with Header() as header:
        right_motor_forward = OutputPin(IN1)
        right_motor_backward = OutputPin(IN2)
        left_motor_forward = OutputPin(IN3)
        left_motor_backward = OutputPin(IN4)

        right_motor_forward.value = False
        right_motor_backward.value = False
        left_motor_forward.value = False
        left_motor_backward.value = False

        pin_ena = PWMOutputPin(ENA, frequency=100)
        pin_ena.value = 0

        pin_enb = PWMOutputPin(ENB, frequency=100)
        pin_enb.value = 0


# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
def forward(speed):

    with Header() as header:
        right_motor_forward = OutputPin(IN1)
        right_motor_backward = OutputPin(IN2)
        left_motor_forward = OutputPin(IN3)
        left_motor_backward = OutputPin(IN4)

        right_motor_forward.value = True
        right_motor_backward.value = False
        left_motor_forward.value = True
        left_motor_backward.value = False

        pin_ena = PWMOutputPin(ENA, frequency=speed + 5)
        pin_ena.value = speed / 100

        pin_enb = PWMOutputPin(ENB, frequency=speed + 5)
        pin_enb.value = speed / 100


# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
def reverse(speed):
    with Header() as header:
        right_motor_forward = OutputPin(IN1)
        right_motor_backward = OutputPin(IN2)
        left_motor_forward = OutputPin(IN3)
        left_motor_backward = OutputPin(IN4)

        right_motor_forward.value = False
        right_motor_backward.value = True
        left_motor_forward.value = False
        left_motor_backward.value = True

        pin_ena = PWMOutputPin(ENA, frequency=speed + 5)
        pin_ena.value = speed / 100

        pin_enb = PWMOutputPin(ENB, frequency=speed + 5)
        pin_enb.value = speed / 100


# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spin_left(speed):

    with Header() as header:
        right_motor_forward = OutputPin(IN1)
        right_motor_backward = OutputPin(IN2)
        left_motor_forward = OutputPin(IN3)
        left_motor_backward = OutputPin(IN4)

        right_motor_forward.value = False
        right_motor_backward.value = True
        left_motor_forward.value = True
        left_motor_backward.value = False

        pin_ena = PWMOutputPin(ENA, frequency=speed + 5)
        pin_ena.value = speed / 100

        pin_enb = PWMOutputPin(ENB, frequency=speed + 5)
        pin_enb.value = speed / 100


# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spin_right(speed):

    with Header() as header:
        right_motor_forward = OutputPin(IN1)
        right_motor_backward = OutputPin(IN2)
        left_motor_forward = OutputPin(IN3)
        left_motor_backward = OutputPin(IN4)

        right_motor_forward.value = True
        right_motor_backward.value = False
        left_motor_forward.value = False
        left_motor_backward.value = True

        pin_ena = PWMOutputPin(ENA, frequency=speed + 5)
        pin_ena.value = speed / 100

        pin_enb = PWMOutputPin(ENB, frequency=speed + 5)
        pin_enb.value = speed / 100

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
