# Test files need to re register themselves for when using shell
import sys
import os
sys.path.insert(1, os.path.abspath(os.path.dirname(__file__)))

from unittest import TestCase
from program import Program
from Util.testing import TestThread
import sys
import time
import os


class TestMain(TestCase):
    def test_movement(self):
        program = Program()

        # Force in some mock-up location data for the Phone module
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(current_dir, 'simulated_location_input.txt')
        program.force_gps_input(open(file_path, 'r').read())

        # Start the main program
        new_thread = TestThread(program)
        new_thread.start()

        print "Simulating Keyboard Input..."
        file_path = os.path.join(current_dir, 'simulatedInput.txt')
        sys.stdin = open(file_path, 'r')

        time.sleep(1)

        print "Simulating Keyboard Interrupt..."
        program.stop()

        time.sleep(1)
        print "Checking if program is done..."

        self.assertEquals(program.is_running(), False)

