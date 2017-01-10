from threading import Thread
from time import sleep
from subprocess import check_output, call, CalledProcessError
from pubsub import pub


class GPS(Thread):
    __GPS_POLL_TIME = 1  # second
    __longitudes = []
    __latitudes = []

    __average_longitude = 0
    __average_latitude = 0

    # dumpsys terminology
    __term_longitude = "mLongitude="
    __term_latitude = "mLatitude="

    # Event names
    EVENT_ON_LATITUDE_CHANGED = "OnLatitudeChanged"
    EVENT_ON_LONGITUDE_CHANGED = "OnLongitudeChanged"

    # Used in Unit-Tests
    testing_input = ""

    def __init__(self):
        try:
            # Boot up adb through USB using the command 'adb usb'
            call(["adb", "usb"])

        # Still allow the thread to properly start and disregard any exceptions for now.
        except OSError:
            pass

        Thread.__init__(self)

    def run(self):

        while not self.name.endswith("--"):
            sleep(self.__GPS_POLL_TIME)

            try:

                # Used in Unit-Tests
                if self.testing_input != "":
                    self.__retrieve_location_information(self.testing_input)
                    self.testing_input = ""

                # Execute command 'adb dumpsys location' and redirect output to our methods.
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

        # First retrieve all location providers.
        # Location provider examples : GPS, Network, Cellular etc...
        for item in raw_location_output.split("\n"):

            # Sometimes the android log will also display a coordinate which is a duplicate.
            if "LOG" in item:
                continue

            if self.__term_latitude in item:
                location_providers.append(item.strip())

        if len(location_providers) < 1:
            return

        # Seems like we have got fresh new data, delete the old first.
        self.__latitudes = []
        self.__longitudes = []

        # Go through every location provider and only get the longitude and latitude values and store them.
        for location_provider in location_providers:
            suffix = location_provider.split(" ")
            for item in suffix:
                if self.__term_latitude in item:
                    latitude_string_value = item.replace(self.__term_latitude, "")
                    self.__latitudes.append(latitude_string_value)

                if self.__term_longitude in item:
                    longitude_string_value = item.replace(self.__term_longitude, "")
                    self.__longitudes.append(longitude_string_value)

        # Now we just have to update our average coordinates
        self.__calculate_and_update_average_coordinates()

    def __calculate_and_update_average_coordinates(self):
        average_longitude = 0
        average_latitude = 0

        for longitude in self.__longitudes:
            average_longitude += float(longitude)

        for latitude in self.__latitudes:
            average_latitude += float(latitude)

        average_longitude /= len(self.__longitudes)
        average_latitude /= len(self.__latitudes)

        # When a change in average latitude/longitude is detected, notify all registered event handlers.

        if average_latitude != self.__average_latitude:
            self.__average_latitude = average_latitude
            pub.sendMessage(self.EVENT_ON_LATITUDE_CHANGED, latitude=self.__average_latitude)

        if average_longitude != self.__average_longitude:
            self.__average_longitude = average_longitude
            pub.sendMessage(self.EVENT_ON_LONGITUDE_CHANGED, longitude=self.__average_longitude)
