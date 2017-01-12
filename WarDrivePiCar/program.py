from threading import Thread
from Controller.controller import Controller
from Controller.keyboard import Keyboard
from Communication.phone_handler import Phone
from Sniffer.sniffer import Sniffer

from time import sleep


class Program:
    __CycleTime = 0.1  # 100 ms
    __isRunning = True
    __KeyboardEnabled = True
    __TestingMode = False

    # Classes should inherit from a Thread and need to join on an KeyboardInterrupt
    __Threads = [
        Sniffer(),
        Controller(),
        Keyboard(),
        Phone()
    ]

    def __init__(self):
        return

    def start(self, testing_mode=False):
        self.__TestingMode = testing_mode

        if not self.__TestingMode:
            yes_or_no = raw_input("Allow keyboard? This will disable the GPS way-point system. ( Y/N )")
            if yes_or_no.capitalize() == "Y":
                self.__KeyboardEnabled = True
            else:
                self.__KeyboardEnabled = False

        self.__start_threads(self.__Threads)

        while self.__isRunning:
            try:
                sleep(self.__CycleTime)

            except KeyboardInterrupt:
                self.stop()
                print "Application stopped by KeyboardInterrupt."
                return

            except Exception as exception:
                print "Exception in 'main': {0}".format(exception)

    def stop(self):
        print "Program stop method called."
        self.__join_threads(self.__Threads)
        self.__isRunning = False

    def is_running(self):
        return self.__isRunning

    # Used for testing purposes. This will force the Phone thread to use mock-up location input data.
    def force_phone_handler_input(self, location_data, sensor_data):
        for thread_instance in self.__Threads:
            if not isinstance(thread_instance, Phone):
                continue

            thread_instance.testing_input_location = location_data
            thread_instance.testing_input_sensor = sensor_data

    def __start_threads(self, threads):
        for thread_instance in threads:
            if not isinstance(thread_instance, Thread):
                continue

            if thread_instance.name.endswith("--"):
                continue

            if isinstance(thread_instance, Keyboard) and not self.__KeyboardEnabled:
                print "Skipping keyboard thread..."
                continue

            if isinstance(thread_instance, Controller):
                waypoint_system_activated = not self.__KeyboardEnabled or self.__TestingMode
                thread_instance.EnableGPSWaypointSystem = waypoint_system_activated
                print "Setting GPS way-point system to : ", waypoint_system_activated

            thread_instance.setName(type(thread_instance).__name__)

            print "Thread '{0}' starting...".format(thread_instance.getName())
            if not thread_instance.isAlive():
                thread_instance.start()
            print "Thread '{0}' started.".format(thread_instance.getName())

    @staticmethod
    def __join_threads(threads):
        for thread_instance in threads:
            if not isinstance(thread_instance, Thread):
                continue

            thread_instance_name = thread_instance.getName()
            thread_instance.setName(thread_instance_name + "--")

            print "Thread '{0}' joining...".format(thread_instance_name)
            if thread_instance.isAlive():
                thread_instance.join()
            print "Thread '{0}' joined.".format(thread_instance_name)
