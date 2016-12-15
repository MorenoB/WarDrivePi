from unittest import TestCase
from Movement.initio import Initio

# Import GPIO library and support mock-up fallback
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('----------------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO can only be run on the RPi. Falling back to mock objects.')
    print('----------------------------------------------------------------------------')
    from Movement import gpio_mock as GPIO
except ImportError:
    print('-------------------------------------------------------------------')
    print(' WARNING: RPi.GPIO library not found. Falling back to mock objects.')
    print('-------------------------------------------------------------------')
    from Movement import gpio_mock as GPIO


class Test__carMovement(TestCase):
    def test_forward(self):
        __carMovement = Initio()
        __carMovement.forward(50)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.LOW)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.LOW)

    def test_init(self):
        __carMovement = Initio()

        self.assertEquals(GPIO.getmode(), GPIO.BCM)


