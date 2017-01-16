from time import sleep
from threading import Thread
from urllib2 import urlopen, URLError, HTTPError
from pubsub import pub
import socket


class InternetConnectionChecker(Thread):
    __LOOP_CYCLE_TIME = 1  # 1 second
    __url = 'http://google.com/'
    __url_response_starts_with = 'http://www.google'

    EVENT_ON_INTERNET_CONNECTION_CHANGED = "OnInternetConnectionChanged"

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        while not self.name.endswith("--"):
            sleep(self.__LOOP_CYCLE_TIME)

            socket.setdefaulttimeout(23)
            try:
                response = urlopen(self.__url)
            except HTTPError:
                self.__changed_internet_connection(False)
            except URLError:
                self.__changed_internet_connection(False)

            # Received response:
            else:
                if response.url.startswith(self.__url_response_starts_with):
                    self.__changed_internet_connection(True)
                    continue  # Internet is up
                else:
                    self.__changed_internet_connection(False)

        print "Thread '{0}' stopped.".format(self.getName())

    def __changed_internet_connection(self, has_internet_connection):
        pub.sendMessage(self.EVENT_ON_INTERNET_CONNECTION_CHANGED, has_internet_connection=has_internet_connection)
