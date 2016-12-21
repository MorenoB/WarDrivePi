from threading import Thread
from time import sleep

from scapy.all import *
from scapy.layers.dot11 import *

import subprocess


class Sniffer(Thread):
    """
    This class sniffs for Access Points and uses the Database class to save this data

    Implements: Thread
    """
    __CPU_CYCLE_TIME = 0.05  # 50 ms

    def __init__(self):
        """

        """
        Thread.__init__(self)
        self.__bssid_history = dict()
        self.__packet_process_queue = Queue.Queue()

    def run(self):
        """

        """

        # Get all WLAN interfaces en set them to monitor mode
        wlan_interfaces = list()
        for wlan_interface in self.__grep_wlan_interfaces():
            if self.__set_monitor_wlan_interface(wlan_interface):
                wlan_interfaces.append(wlan_interface)

        if len(wlan_interfaces) == 0:
            print "{0} -> No (valid) WLAN interfaces detected... Joining thread '{0}'.".format(self.name)
            return

        # Start sniffing on all WLAN interfaces
        print "{0} -> Sniffing is done by WLAN interfaces: {1}.".format(self.name, wlan_interfaces)
        while not self.name.endswith("--"):
            try:
                sleep(self.__CPU_CYCLE_TIME)

                for wlan_interface in wlan_interfaces:
                    sniff(iface=wlan_interface, count=1, prn=self.__radio_tap_handler, timeout=1)

            except Scapy_Exception as exception:
                print "Scapy exception in thread '{0}': {1}".format(self.name, exception)

            except Exception as exception:
                print "Exception in thread '{0}': {1}".format(self.name, exception)

    def __grep_wlan_interfaces(self):
        """
        Get all WLAN interfaces and return them in a list

        Requires: Unix
        """
        # ifconfig -s | cut -d " " -f1 | grep wlan
        command = subprocess.Popen(["ifconfig", "-s"], stdout=subprocess.PIPE)
        command = subprocess.Popen(["cut", "-d", " ", "-f1"], stdin=command.stdout, stdout=subprocess.PIPE)
        command = subprocess.Popen(["grep", "wlan"], stdin=command.stdout, stdout=subprocess.PIPE)

        (std_out_data, std_error_data) = command.communicate()
        if std_error_data is None:
            wlan_interfaces = std_out_data.split()
            print "{0} -> Detected WLAN interfaces: {1}".format(self.name, wlan_interfaces)
            return wlan_interfaces
        else:
            print "{0} -> Error while detecting WLAN interfaces: {1}".format(self.name, std_error_data)
            return list()

    def __set_monitor_wlan_interface(self, wlan_interface):
        """
        Set all WLAN interfaces from the list into monitor mode

        Requires: Unix
        """

        # Force interface to be a WLAN interface
        if not isinstance(wlan_interface, str):
            print "{0} -> Not a WLAN interface string: {1}".format(self.name, wlan_interface)
            return False
        if not wlan_interface.startswith("wlan"):
            print "{0} -> Not a WLAN interface: {1}".format(self.name, wlan_interface)
            return False

        # ifconfig <interface> down
        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", wlan_interface, "down"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing WLAN interface '{1}' down: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        # iwconfig <interface> mode Monitor
        (std_out_data, std_error_data) = subprocess.Popen(["iwconfig", wlan_interface, "mode", "Monitor"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while setting WLAN interface '{1}' in monitor mode: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        # ifconfig <interface> up
        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", wlan_interface, "up"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing WLAN interface '{1}' back up: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        print "{0} -> WLAN interface '{1}' configured succesfully.".format(self.name, wlan_interface)
        return True

    def __radio_tap_handler(self, radio_tap):
        """
        Dissects and pushes data from Radiotap packets to the Database class
        """

        # Force packet to be RadioTap
        if not isinstance(radio_tap, RadioTap):
            print "Filtered '{0}' packet!".format(type(radio_tap).__name__)
            return

        print "---{0}---".format(radio_tap.name)
        print radio_tap.sprintf("%RadioTap.fields%")

        # Force RadioTap's payload to be Dot11
        dot11 = radio_tap.payload
        if not isinstance(dot11, Dot11):
            print "Filtered '{0}' layer!".format(type(dot11).__name__)
            return

        print "\t{0}".format(dot11.sprintf("%Dot11.fields%"))

        # Force Dot11's payload to be a Dot11 subtype
        dot11_subtype = dot11.payload
        if not isinstance(dot11_subtype, (
            Dot11AssoReq, Dot11AssoResp, Dot11ReassoReq, Dot11ReassoResp, Dot11ProbeReq, Dot11ProbeResp, Dot11Beacon,
                Dot11ATIM, Dot11Disas, Dot11Auth, Dot11Deauth, Dot11WEP)):
            print "Filtered '{0}' Dot11 subtype!".format(type(dot11_subtype).__name__)
            return

        print "\t\t{0}".format(dot11.sprintf("%{0}.fields%".format(type(dot11_subtype).__name__)))

        # Loop trough Dot11 subtype's payload until it is NoPayload
        dot11_elt = dot11_subtype.payload
        while not isinstance(dot11_elt, NoPayload):
            try:
                # Force Dot11 subtype's payload to be a Dot11Elt
                if not isinstance(dot11_elt, Dot11Elt):
                    print "Filtered '{0}' element!".format(type(dot11_elt).__name__)
                    continue

                print "\t\t\t{0}".format(dot11_elt.sprintf("%Dot11Elt.fields%"))
                # print "{0}\t{1}".format(dot11_elt.fields_desc[0].i2s[dot11_elt.ID], dot11_elt.info)
            except KeyError:
                print "Filtered '{0}' element field!".format(dot11_elt.ID)
            finally:
                dot11_elt = dot11_elt.payload

        print "---=---\n"
