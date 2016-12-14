# Mock-up data for when RPi.GPIO is not present.
BOARD = "board"
BCM = "bcm"
OUT = "out"
IN = "in"


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
        print "PWM ", self._pin, ":", self._frequency

    def ChangeDutyCycle(self,duty_cycle):
        self._duty_cycle = duty_cycle
        print "Changed duty cycle to ", self._duty_cycle

    def ChangeFrequency(self, frequency):
        self._frequency = frequency
        print "Changed frequency to ", self._frequency


def output(pin, value):
    print pin, ":", value


def setmode(mode):
    print mode


def setup(pin, value):
    print pin, ":", value


def cleanup():
    print "clean-up"


def LOW():
    return "LOW"


def HIGH():
    return "HIGH"


def setwarnings(value):
    return "Setting GPIO warnings to ", value