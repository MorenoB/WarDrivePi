from threading import Thread
from time import sleep
from subprocess import check_output, call


class GPS(Thread):
    __GPS_POLL_TIME = 1  # second

    def __init__(self):
        # adb usb
        try:
            call(["adb", "usb"])
        # Still allow the thread to properly start and disregard any exceptions for now.
        except OSError:
            pass

        Thread.__init__(self)

    def run(self):

        while not self.name.endswith("--"):
            sleep(self.__GPS_POLL_TIME)

            # adb dumpsys location > Dumps/location.txt
            try:
                raw_location_output = check_output(["adb", "shell", "dumpsys", "location"])
                self.__reformat_location_output(raw_location_output)
            except OSError:
                print "'adb' Command not properly installed on this machine! Shutting down GPS module..."
                break

        print "Thread '{0}' stopped.".format(self.getName())

    @staticmethod
    def __reformat_location_output(raw_location_output):
        location_providers = []
        for item in raw_location_output.split("\n"):
            if "mLatitude=" in item:
                location_providers.append(item.strip())

        print location_providers

        for location_provider in location_providers:
            suffix = location_provider.split(" ")
            for item in suffix:
                if "mLatitude=" in item:
                    item.replace("mLatitude=", "")
                    print item

                if "mLongitude=" in item:
                    item.replace("mLongitude=", "")
                    print item

