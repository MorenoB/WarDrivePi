from threading import Thread
from time import sleep
from subprocess import check_output, call, CalledProcessError


class GPS(Thread):
    __GPS_POLL_TIME = 1  # second
    __longitudes = []
    __latitudes = []

    # Used in Unit-Tests
    testing_input = ""

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

                # Used in Unit-Tests
                if self.testing_input != "":
                    self.__retrieve_location_information(self.testing_input)
                    self.testing_input = ""

                raw_location_output = check_output(["adb", "shell", "dumpsys", "location"])
                self.__retrieve_location_information(raw_location_output)
            except OSError:
                print "'adb' Command not properly installed on this machine! Shutting down GPS module..."
                break
            except CalledProcessError:
                print "Device was not found! Retrying on next loop update..."
                pass  # In case the device was not found, retry again!

        print "Thread '{0}' stopped.".format(self.getName())

    def __retrieve_location_information(self, raw_location_output):
        location_providers = []
        for item in raw_location_output.split("\n"):

            # Sometimes the android log will also display a coordinate which is a duplicate.
            if "LOG" in item:
                continue

            if "mLatitude=" in item:
                location_providers.append(item.strip())

        if len(location_providers) < 1:
            return

        self.__latitudes = []
        self.__longitudes = []

        for location_provider in location_providers:
            suffix = location_provider.split(" ")
            for item in suffix:
                if "mLatitude=" in item:
                    latitude_string_value = item.replace("mLatitude=", "")
                    self.__latitudes.append(latitude_string_value)

                if "mLongitude=" in item:
                    longitude_string_value = item.replace("mLongitude=", "")
                    self.__longitudes.append(longitude_string_value)

        self.__print_average_coordinates()

    def __print_average_coordinates(self):
        average_longitude = 0
        average_latitude = 0

        for longitude in self.__longitudes:
            average_longitude += float(longitude)

        for latitude in self.__latitudes:
            average_latitude += float(latitude)

        average_longitude /= len(self.__longitudes)
        average_latitude /= len(self.__latitudes)

        print "Average latitude : ", average_latitude
        print "Average longitude : ", average_longitude
