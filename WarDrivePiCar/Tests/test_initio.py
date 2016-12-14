from unittest import TestCase
import sys
sys.path.append("/WarDrivePiCar/")
from Movement import initio

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


class TestInitio(TestCase):
    def test_forward(self):
        initio.init()
        initio.forward(50)

        self.assertEquals(GPIO.input(initio.IN1), GPIO.HIGH)
        self.assertEquals(GPIO.input(initio.IN2), GPIO.LOW)

        self.assertEquals(GPIO.input(initio.IN3), GPIO.HIGH)
        self.assertEquals(GPIO.input(initio.IN4), GPIO.LOW)

    def test_init(self):
        initio.init()

        self.assertEquals(GPIO.getmode(), GPIO.BCM)


