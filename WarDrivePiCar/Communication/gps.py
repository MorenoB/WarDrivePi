from threading import Thread
from time import sleep
from subprocess import call


class GPS(Thread):
    __GPS_POLL_TIME = 0.5  # 0.5 second

    def __init__(self):
        # adb usb
        try:
            call(["adb", "usb"])
        # Still allow the thread to properly start and disregard any exceptions for now.
        except WindowsError:
            pass
        except OSError:
            pass

        Thread.__init__(self)

    def run(self):

        # Program Loop
        while not self.name.endswith("--"):
            # adb dumpsys location > Dumps/location.txt
            try:
                call(["adb", "dumpsys", "location"])
            except WindowsError:
                print "'adb' Command not properly installed on this Windows machine! Shutting down GPS module..."
                break
            except OSError:
                print "'adb' Command not properly installed on this machine! Shutting down GPS module..."
                break
            sleep(self.__GPS_POLL_TIME)

        print "Thread '{0}' stopped.".format(self.getName())
