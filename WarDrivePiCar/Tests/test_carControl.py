from unittest import TestCase
from Movement.CarControl import CarControl

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

    def test_init(self):
        __carMovement = CarControl()

        self.assertEquals(GPIO.getmode(), GPIO.BCM)

        __carMovement.cleanup()

    def test_stop(self):
        __carMovement = CarControl()

        __carMovement.stop()

        __carMovement.cleanup()
        self.skipTest("Due to unexposed functions/variables.")

    def test_cleanup(self):
        __carMovement = CarControl()

        __carMovement.cleanup()
        self.skipTest("Due to unexposed functions/variables.")

    def test_forward(self):
        __carMovement = CarControl()
        __carMovement.forward(15)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.LOW)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.LOW)

        __carMovement.cleanup()

    def test_turn_lef_forward(self):
        __carMovement = CarControl()
        __carMovement.turn_left()

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.LOW)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.LOW)

        __carMovement.cleanup()

    def test_turn_right_reverse(self):
        __carMovement = CarControl()
        __carMovement.turn_right(True)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.HIGH)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.HIGH)

        __carMovement.cleanup()

    def test_reverse(self):
        __carMovement = CarControl()
        __carMovement.reverse(15)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.HIGH)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.HIGH)

        __carMovement.cleanup()

    def test_spin_left(self):
        __carMovement = CarControl()
        __carMovement.spin_left(15)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.HIGH)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.LOW)

        __carMovement.cleanup()

    def test_spin_right(self):
        __carMovement = CarControl()
        __carMovement.spin_right(15)

        self.assertEquals(GPIO.input(__carMovement.IN1), GPIO.HIGH)
        self.assertEquals(GPIO.input(__carMovement.IN2), GPIO.LOW)

        self.assertEquals(GPIO.input(__carMovement.IN3), GPIO.LOW)
        self.assertEquals(GPIO.input(__carMovement.IN4), GPIO.HIGH)

        __carMovement.cleanup()
