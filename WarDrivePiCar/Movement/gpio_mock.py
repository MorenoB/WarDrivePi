# Mock-up data for when RPi.GPIO is not present.
BOARD = "board"
BCM = "bcm"
OUT = "out"
IN = "in"
HIGH = "HIGH"
LOW = "LOW"
FALLING = "FALLING"

__pin_state_dict = {}
__mode = BOARD


def output(pin, value):
    __pin_state_dict[pin] = value
    print "Setting pin ", pin, ":", value


def setmode(mode):
    global __mode
    __mode = mode
    print "Setting mode to ", __mode


def setup(pin, value):
    __pin_state_dict[pin] = LOW
    print "Setup pin ", pin


def cleanup():
    print "clean-up"


def setwarnings(value):
    return "Setting GPIO warnings to ", value


def input(pin):
    return __pin_state_dict.get(pin)


def getmode():
    return __mode


def add_event_detect(param, FALLING, callback):
    print "added event callback"
    callable(callback)


class PWM:
    _frequency = 0
    _value = 0
    _pulse = 0
    _pin = 0
    _duty_cycle = 0

    def __init__(self, pin, frequency=50.0, value=0.0):
        self._frequency = frequency
        self._value = value
        self._pulse = frequency
        self._pin = pin

    def start(self, value=0.0):
        self._value = value
        print "Starting PWM pin ", self._pin, " frequency ", self._frequency

    def ChangeDutyCycle(self, duty_cycle):
        self._duty_cycle = duty_cycle
        print "Changed duty cycle to ", self._duty_cycle

    def ChangeFrequency(self, frequency):
        self._frequency = frequency
        print "Changed frequency to ", self._frequency