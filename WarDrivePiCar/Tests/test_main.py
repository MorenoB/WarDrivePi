from unittest import TestCase
from pynput.keyboard import Controller, Key
from WarDrivePiCar import Main
import time
from threading import Thread


class TestMain(TestCase):
    def test_movement(self):
        program = Main.Main()
        new_thread = TestThread(program)
        new_thread.start()

        # Wait a some time until we simulate key presses
        time.sleep(1)

        # Simulate keyboard presses to test our keyboard listeners inside our Controller module.
        simulated_keyboard = Controller()

        simulated_keyboard.press(Key.up)
        simulated_keyboard.release(Key.up)

        simulated_keyboard.press(Key.down)
        simulated_keyboard.release(Key.down)

        simulated_keyboard.press(Key.left)
        simulated_keyboard.release(Key.left)

        simulated_keyboard.press(Key.right)
        simulated_keyboard.release(Key.right)

        print "Simulating shutdown keyboard event..."
        simulated_keyboard.press(Key.esc)
        simulated_keyboard.release(Key.esc)

        # Wait for program to terminate.
        time.sleep(1)

        print "Checking if program is done..."
        self.assertEquals(program.is_running(), False)

        program.stop()


class TestThread(Thread):
    __thread_obj = None

    def __init__(self, thread_obj):
        Thread.__init__(self)
        self.__thread_obj = thread_obj

    def run(self):
        self.__thread_obj.start()
