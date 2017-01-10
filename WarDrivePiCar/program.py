from threading import Thread
from Controller.controller import Controller
from Controller.keyboard import Keyboard
from Communication.gps import GPS
# from Sniffer.Sniffer import Sniffer

from time import sleep


class Program:
    __CycleTime = 0.1  # 100 ms
    __isRunning = True

    # Classes should inherit from a Thread and need to join on an KeyboardInterrupt
    __Threads = [
        # Sniffer()
        Controller(),
        Keyboard(),
        GPS()
    ]

    def __init__(self):
        return

    def start(self):

        # print "Application started... {0}".format("(w/ REMOTE DEBUGGING [{0}])".format(SysArgv.items['trace'])
        #                                          if pydevd.connected else str())

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

    @staticmethod
    def __start_threads(threads):
        for thread_instance in threads:
            if not isinstance(thread_instance, Thread):
                continue

            if thread_instance.name.endswith("--"):
                continue

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
