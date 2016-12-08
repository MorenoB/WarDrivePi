from threading import Thread
from time import sleep

import subprocess

from scapy.all import *
from scapy.layers.dot11 import *


class Sniffer(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms

    def __init__(self):
        Thread.__init__(self)
        self.__mac_history = list()
        self.__packet_process_queue = Queue.Queue()

    def run(self):

        wlan_interfaces = list()
        for wlan_interface in self.__grep_wlan_interfaces():
            if self.__set_monitor_wlan_interface(wlan_interface):
                wlan_interfaces.append(wlan_interface)

        if len(wlan_interfaces) == 0:
            print "{0} -> No (valid) WLAN interfaces detected... Joining thread '{0}'.".format(self.name)
            return

        print "{0} -> Sniffing is done by WLAN interfaces: {1}.".format(self.name, wlan_interfaces)
        while not self.name.endswith("--"):
            try:
                sleep(self.__CPU_CYCLE_TIME)

                for wlan_interface in wlan_interfaces:
                    sniff(iface=wlan_interface, count=1, prn=self.__packet_handler, timeout=1)

            except Scapy_Exception as exception:
                print "Scapy exception in thread '{0}': {1}".format(self.name, exception)

            except Exception as exception:
                print "Exception in thread '{0}': {1}".format(self.name, exception)

    def __grep_wlan_interfaces(self):
        command = subprocess.Popen(["ifconfig", "-s"], stdout=subprocess.PIPE)
        command = subprocess.Popen(["cut", "-d", "\" \"", "-f1"], stdin=command.stdout, stdout=subprocess.PIPE)
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
        if not isinstance(wlan_interface, str):
            print "{0} -> Not a WLAN interface string: {1}".format(self.name, wlan_interface)
            return False
        if not wlan_interface.startswith("wlan"):
            print "{0} -> Not a WLAN interface: {1}".format(self.name, wlan_interface)
            return False

        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", wlan_interface, "down"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing WLAN interface '{1}' down: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        (std_out_data, std_error_data) = subprocess.Popen(["iwconfig", wlan_interface, "mode", "Monitor"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while setting WLAN interface '{1}' in monitor mode: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", wlan_interface, "up"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing WLAN interface '{1}' back up: {2}" \
                .format(self.name, wlan_interface, std_error_data)
            return False

        print "{0} -> WLAN interface '{1}' configured succesfully.".format(self.name, wlan_interface)
        return True

    def __packet_handler(self, pkt):
        if not isinstance(pkt, Packet):
            pkt = Packet()
        if pkt == Packet():
            return
        if not pkt.haslayer(Dot11):
            return

        if pkt.type == 0 and pkt.subtype == 8:
            if pkt.addr2 not in self.__mac_history:
                self.__mac_history.append(pkt.addr2)
                self.__packet_process_queue.put(pkt)
                print("{0} -> New Access Point: MAC='{1}', SSID='{2}'".format(self.name, pkt.addr2, pkt.info))
