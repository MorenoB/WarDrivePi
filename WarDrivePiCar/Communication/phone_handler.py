from threading import Thread
from time import sleep
from subprocess import check_output, call, CalledProcessError
from datetime import datetime

import psycopg2
from pubsub import pub
from Util.extensions import *


class Phone(Thread):
    __CPU_CYCLE_TIME = 0.25  # 250 ms
    __CONNECTION_STRING = "dbname=packets user=postgres password=__Raspi2DB host=localhost port=5432"
    __COMPASS_DIFFERENCE = 45  # Calibrated difference, how is the phone attached to the car?
    # Right now it is faced west relative to the position of the car itself so all the input need to be 45

    __USING_LG4 = True

    __latitudes = []
    __longitudes = []
    __altitudes = []
    __accuracies = []

    __average_latitude = 0
    __average_longitude = 0
    __average_altitude = 0
    __average_accuracy = 0
    __averages_updated = datetime.min

    # dumpsys terminology
    __term_latitude = "mLatitude="
    __term_longitude = "mLongitude="
    __term_altitude = "mAltitude="
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
        if self.__USING_LG4:
            call(["adb", "logcat", "-c"])
            raw_sensor_output = check_output(["adb", "logcat", "-d", "Compass:D", "*:S"])

        else:
            raw_sensor_output = check_output(["adb", "shell", "dumpsys", "sensorservice"])
        self.__retrieve_compass_information_from_sensor_service(raw_sensor_output)

    def __get_gps_data(self):

        # Used in Unit-Tests
        if self.testing_input_location != "":
            self.__retrieve_location_information(self.testing_input_location)
            self.testing_input_location = ""
            return

        # Execute command 'adb dumpsys location' and redirect output to our methods.
        if self.__USING_LG4:
            raw_location_output = check_output(["adb", "shell", "dumpsys", "location", "|", "grep", "ready=true"])
        else:
            raw_location_output = check_output(["adb", "shell", "dumpsys", "location"])
        self.__retrieve_location_information(raw_location_output)

    def __retrieve_compass_information_from_sensor_service(self, raw_sensor_data):
        if self.__USING_LG4:
            self.__retrieve_compass_information_lg4(raw_sensor_data)
        else:
            self.__retrieve_compass_information_samsung(raw_sensor_data)

    def __retrieve_compass_information_lg4(self, raw_sensor_data):
        for line in raw_sensor_data.split("\n"):

            if "AngleInDegrees" in line:
                # Find the value and use calibrated values stated in "__COMPASS_DIFFERENCE"
                found_compass_value = find_between(line, "[", "]")
                compass_value = round(float(found_compass_value) + float(self.__COMPASS_DIFFERENCE))
                compass_value = convert_int_to_degrees(compass_value)

                pub.sendMessage(self.EVENT_ON_COMPASS_CHANGED, compass=compass_value)

    def __retrieve_compass_information_samsung(self, raw_sensor_data):

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

    def __retrieve_location_information_samsung_phone(self, raw_location_data):
        multi_value_lines = []

        # First retrieve all location providers.
        # Location provider examples : Phone, Network, Cellular etc...
        for item in raw_location_data.split("\n"):

            # Sometimes the android log will also display a coordinate which is a duplicate.
            if "LOG" in item:
                continue

            # Latitude and longitude values are on the same line. This is considered a 'multi-value line' which will be
            # stripped later on.
            if self.__term_latitude in item:
                multi_value_lines.append(item.strip())

            if self.__term_accuracy in item:
                multi_value_lines.append(item.strip())

        if len(multi_value_lines) < 1:
            return

        # Seems like we have got fresh new data, delete the old first.
        self.__latitudes = []
        self.__longitudes = []
        self.__altitudes = []
        self.__accuracies = []

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

                if self.__term_altitude in item:
                    altitude_string_value = item.replace(self.__term_altitude, "")
                    self.__altitudes.append(altitude_string_value)

                if self.__term_accuracy in item:
                    accuracy_string_value = item.replace(self.__term_accuracy, "")
                    self.__accuracies.append(accuracy_string_value)

    def __retrieve_location_information_lg4(self, raw_location_data):
        for line in raw_location_data.split("\n"):
            if "Location" in line:
                found_longitude = find_between(line, "fused ", ",")
                found_latitude = find_between(line, ",", " acc")
                found_altitude = find_between(line, "alt=", " vel=")
                found_accuracy = find_between(line, "acc=", " et=")

                self.__longitudes.append(found_longitude)
                self.__latitudes.append(found_latitude)
                self.__altitudes.append(found_altitude)
                self.__accuracies.append(found_accuracy)

    def __retrieve_location_information(self, raw_location_data):
        if self.__USING_LG4:
            self.__retrieve_location_information_lg4(raw_location_data)
        else:
            self.__retrieve_location_information_samsung_phone(raw_location_data)

        # Now we just have to update our average coordinates
        self.__calculate_and_update_average_values()

    def __calculate_and_update_average_values(self):
        average_latitude = 0
        average_longitude = 0
        average_altitude = 0
        average_accuracy = 0

        if len(self.__longitudes) > 0:
            for longitude in self.__longitudes:
                average_longitude += float(longitude)
            average_longitude /= len(self.__longitudes)

        if len(self.__latitudes) > 0:
            for latitude in self.__latitudes:
                average_latitude += float(latitude)
            average_latitude /= len(self.__latitudes)

        if len(self.__altitudes) > 0:
            for altitude in self.__altitudes:
                average_altitude += float(altitude)
            average_latitude /= len(self.__latitudes)

        if len(self.__accuracies) > 0:
            for accuracy in self.__accuracies:
                average_accuracy += float(accuracy)
            average_accuracy /= len(self.__accuracies)

        # When a change in average values is detected, notify all registered event listeners and commit to the database.
        if average_latitude != self.__average_latitude \
                or average_longitude != self.__average_longitude \
                or average_altitude != self.__average_altitude:

            # Set new averages
            self.__average_latitude = average_latitude
            self.__average_longitude = average_longitude
            self.__average_altitude = average_altitude
            self.__average_accuracy = average_accuracy
            self.__averages_updated = datetime.now()

            pub.sendMessage(self.EVENT_ON_LOCATION_CHANGED,
                            longitude=self.__average_longitude,
                            latitude=self.__average_latitude,
                            altitude=self.__average_altitude,
                            accuracy=self.__average_accuracy)

            self.__commit_changed_average_values()

    def __commit_changed_average_values(self):
        connection = None
        cursor = None

        try:
            # Set up connection
            connection = psycopg2.connect(self.__CONNECTION_STRING)
            cursor = connection.cursor()

            # Prepare query and parameters for GPS data
            sensor_gps_query = """
                INSERT INTO sensor_gps(latitude, longitude, altitude, accuracy, timestamp)
                VALUES({0}, {1}, {2}, {3}, {4});
                """ \
                .format("%(latitude)s", "%(longitude)s", "%(altitude)s", "%(accuracy)s", "%(timestamp)s") \
                .replace("  ", "")
            sensor_gps_parameters = {
                'latitude': self.__average_latitude,
                'longitude': self.__average_longitude,
                'altitude': self.__average_altitude,
                'accuracy': self.__average_accuracy,
                'timestamp': self.__averages_updated
            }

            # Execute
            cursor.execute(sensor_gps_query, sensor_gps_parameters)
            print "{0} -> Added sensor GPS data for '(Lat:{1}, Long:{2})'!"\
                .format(self.name, self.__average_latitude, self.__average_longitude)

            # Commit
            connection.commit()
        except Exception as exception:
            print "Exception in thread '{0}': {1}".format(self.name, exception)

            # Rollback on ANY exception
            if connection is not None:
                connection.rollback()
        finally:
            # Close the connections
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
