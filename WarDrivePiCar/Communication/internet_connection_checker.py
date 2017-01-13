from time import sleep
from threading import Thread
from urllib2 import urlopen, URLError, HTTPError
from pubsub import pub
import socket


class InternetConnectionChecker(Thread):
    __LOOP_CYCLE_TIME = 1  # 1 second
    __url = 'http://google.com/'
    __url_response_starts_with = 'http://www.google'

    EVENT_ON_LOST_INTERNET_CONNECTION = "OnLostInternetConnection"
    EVENT_ON_HAS_INTERNET_CONNECTION = "OnHasInternetConnection"

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        while not self.name.endswith("--"):
            sleep(self.__LOOP_CYCLE_TIME)

            socket.setdefaulttimeout(23)
            try:
                response = urlopen(self.__url)
            except HTTPError:
                self.__on_lost_internet_connection()
            except URLError:
                self.__on_lost_internet_connection()

            # Received response:
            else:
                if response.url.startswith(self.__url_response_starts_with):
                    self.__on_has_internet_connection()
                    continue  # Internet is up
                else:
                    self.__on_lost_internet_connection()

        print "Thread '{0}' stopped.".format(self.getName())

    def __on_lost_internet_connection(self):
        pub.sendMessage(self.EVENT_ON_LOST_INTERNET_CONNECTION)
        print "Lost internet!"

    def __on_has_internet_connection(self):
        pub.sendMessage(self.EVENT_ON_HAS_INTERNET_CONNECTION)
        print "Has internet!"
