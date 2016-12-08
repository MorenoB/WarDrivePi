from threading import Thread

from scapy.all import *
from scapy.layers.dot11 import Dot11


class Sniffer(Thread):

    ap_list = []

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while not self.name.endswith("--"):
            try:
                sniff(iface="wlan0", count=1, prn=self.packet_handler, timeout=1)

            except Scapy_Exception as exception:
                print "Scapy exception in thread '{0}': {1}".format(self.name, exception)

            except Exception as exception:
                print "Exception in thread '{0}': {1}".format(self.name, exception)


    def packet_handler(self, pkt):
        if not isinstance(pkt, Packet):
            pkt = Packet()

        if pkt.haslayer(Dot11):
            if pkt.type == 0 and pkt.subtype == 8:
                if pkt.addr2 not in self.ap_list:
                    self.ap_list.append(pkt.addr2)
                    print("AP MAC: %s with SSID: %s " % (pkt.addr2, pkt.info))



