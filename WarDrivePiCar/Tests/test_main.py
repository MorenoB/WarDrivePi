from unittest import TestCase
from WarDrivePiCar.Main import Main
from WarDrivePiCar.Util.TestingUtils import TestThread
import sys
import time

class TestMain(TestCase):
    def test_movement(self):
        program = Main()

        new_thread = TestThread(program)
        new_thread.start()

        stdin = sys.stdin

        try:
            # Simulate keyboard presses to test our keyboard listeners inside our Controller module.
            # os.write(0, "\x1b[A")

            sys.stdin = open('simulatedInput.txt', 'r')

            time.sleep(1)

            print "Simulating Keyboard Interrupt..."
            program.stop()

        except IOError:
            pass

        print "Checking if program is done..."

        # sys.stdin = stdin
        self.assertEquals(program.is_running(), False)

