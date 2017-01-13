from threading import Thread
from time import sleep
from subprocess import check_output, call, CalledProcessError
from pubsub import pub
from Util.extensions import find_between, clamp, convert_int_to_degrees


class Phone(Thread):
    __CPU_CYCLE_TIME = 0.25  # 250 ms
    __longitudes = []
    __latitudes = []
    __accuracies = []

    __average_longitude = 0
    __average_latitude = 0
    __average_accuracy = 0

    # dumpsys terminology
    __term_longitude = "mLongitude="
    __term_latitude = "mLatitude="
    __term_accuracy = "mAccuracy="

    # Event names
    EVENT_ON_LOCATION_CHANGED = "OnLocationChanged"
    EVENT_ON_COMPASS_CHANGED = "OnCompassChanged"

    # Used in Unit-Tests
    testing_input_location = ""
    testing_input_sensor = ""

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
            sleep(self.__CPU_CYCLE_TIME)

            try:

                self.__get_gps_data()
                self.__get_compass_data()

            except OSError:
                print "'adb' Command not properly installed on this machine! Shutting down Phone module..."
                break
            except CalledProcessError:
                print "Device was not found! Retrying on next loop update..."
                pass  # In case the device was not found, retry again!

        self.__shutdown_phone_connection()
        print "Thread '{0}' stopped.".format(self.getName())

    @staticmethod
    def __shutdown_phone_connection():
        try:
            # 'adb shell stop' to stop all current emulators
            call(["adb", "shell", "stop"])
            # 'adb shell exit' to make sure we exit all emulating processes
            call(["adb", "shell", "exit"])

        # If this OS does not support adb calls, just return
        except OSError:
            return

    def __get_compass_data(self):

        # Used in Unit-Tests
        if self.testing_input_sensor != "":
            self.__retrieve_compass_information_from_sensor_service(self.testing_input_sensor)
            self.testing_input_sensor = ""
            return

        # Execute command 'adb shell dumpsys sensorservice' and redirect output to our methods.
        raw_sensor_output = check_output(["adb", "shell", "dumpsys", "sensorservice"])
        self.__retrieve_compass_information_from_sensor_service(raw_sensor_output)

    def __get_gps_data(self):

        # Used in Unit-Tests
        if self.testing_input_location != "":
            self.__retrieve_location_information(self.testing_input_location)
            self.testing_input_location = ""
            return

        # Execute command 'adb dumpsys location' and redirect output to our methods.
        raw_location_output = check_output(["adb", "shell", "dumpsys", "location"])
        self.__retrieve_location_information(raw_location_output)

    def __retrieve_compass_information_from_sensor_service(self, raw_sensor_data):

        for line in raw_sensor_data.split("\n"):

            # Prevent us from picking the wrong line, android tends to display the outdated logs as wel.
            if "handle" in line:
                continue

            if "Mag & Acc" in line:
                # Retrieve the compass value and send message to all compass event listeners with a rounded int value
                non_spaced_line = line.replace(" ", "")
                compass_value = find_between(non_spaced_line, "last=<", ",")
                compass_value = round(float(compass_value))

                # Make sure we work with correct degree numbers. Between 0 and 359, both inclusive.
                compass_value = convert_int_to_degrees(compass_value)

                pub.sendMessage(self.EVENT_ON_COMPASS_CHANGED, compass=compass_value)

    def __retrieve_location_information(self, raw_location_data):
        multi_value_lines = []

        # First retrieve all location providers.
        # Location provider examples : Phone, Network, Cellular etc...
        for item in raw_location_data.split("\n"):

            # Sometimes the android log will also display a coordinate which is a duplicate.
            if "LOG" in item:
                continue

            # Longitude and latitude values are on the same line. This is considered a 'multi-value line' which will be
            # stripped later on.
            if self.__term_latitude in item:
                multi_value_lines.append(item.strip())

            if self.__term_accuracy in item:
                multi_value_lines.append(item.strip())

        if len(multi_value_lines) < 1:
            return

        # Seems like we have got fresh new data, delete the old first.
        self.__accuracies = []
        self.__latitudes = []
        self.__longitudes = []

        # Go through every multi-value line and only get the longitude and latitude values and store them.
        for line in multi_value_lines:
            suffix = line.split(" ")
            for item in suffix:
                if self.__term_latitude in item:
                    latitude_string_value = item.replace(self.__term_latitude, "")
                    self.__latitudes.append(latitude_string_value)

                if self.__term_longitude in item:
                    longitude_string_value = item.replace(self.__term_longitude, "")
                    self.__longitudes.append(longitude_string_value)

                if self.__term_accuracy in item:
                    accuracy_string_value = item.replace(self.__term_accuracy, "")
                    self.__accuracies.append(accuracy_string_value)

        # Now we just have to update our average coordinates
        self.__calculate_and_update_average_values()

    def __calculate_and_update_average_values(self):
        average_longitude = self.__average_longitude
        average_latitude = self.__average_latitude
        average_accuracy = self.__average_accuracy

        if len(self.__longitudes) > 0:
            for longitude in self.__longitudes:
                average_longitude += float(longitude)
            average_longitude /= len(self.__longitudes)

        if len(self.__latitudes) > 0:
            for latitude in self.__latitudes:
                average_latitude += float(latitude)
            average_latitude /= len(self.__latitudes)

        if len(self.__accuracies) > 0:
            for accuracy in self.__accuracies:
                average_accuracy += float(accuracy)
            average_accuracy /= len(self.__accuracies)

        # When a change in average values is detected, notify all registered event listeners.
        if average_latitude != self.__average_latitude \
                or average_longitude != self.__average_longitude \
                or average_accuracy != self.__average_accuracy:
            self.__average_latitude = average_latitude
            self.__average_longitude = average_longitude
            self.__average_accuracy = average_accuracy

            pub.sendMessage(self.EVENT_ON_LOCATION_CHANGED, longitude=self.__average_longitude,
                            latitude=self.__average_latitude, accuracy=self.__average_accuracy)
