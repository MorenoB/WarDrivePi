from ast import literal_eval
from datetime import datetime

import psycopg2
from scapy.all import *
from scapy.layers.dot11 import *

from threading import Thread
from time import sleep

import subprocess


class Sniffer(Thread):
    """
    This class sniffs for Access Points and uses the Database class to save this data

    Implements: Thread
    """
    __CPU_CYCLE_TIME = 0.05  # 50 ms

    __INTERFACE_STARTS_WITH = "sniffer"

    __CONNECTION_STRING = "dbname=Packets user=postgres password=__Raspi2DB host=localhost port=5432"
    """
    PARAMETER:      DESCRIPTION:
    dbname          The database name (only in the dsn string)
    database        The database name (only as keyword argument)
    user            User name used to authenticate
    password        Password used to authenticate
    host            Database host address (defaults to UNIX socket if not provided)
    port            Connection port number (defaults to 5432 if not provided)
    """

    __BITWISE_LENGTHS = {
        'cap': 32,
        'FCfield': 8,
        'present': 32
    }

    def __init__(self):
        """

        """
        Thread.__init__(self)
        self.__committed_bss_ids = list()
        self.__notified_duplicate_bss_ids = list()

    def run(self):
        """

        """

        # Get all sniffer interfaces en set them to monitor mode
        sniffer_interfaces = list()

        try:
            for sniffer_interface in self.__grep_sniffer_interfaces():
                if self.__set_monitor_mode_for_interface(sniffer_interface):
                    sniffer_interfaces.append(sniffer_interface)
        except OSError:
            print "{0} -> Not supported on this OS, shutting down {0}...".format(self.name)
            return

        if len(sniffer_interfaces) == 0:
            print "{0} -> No (valid) sniffer interfaces detected... Joining thread '{0}'.".format(self.name)
            return

        self.__committed_bss_ids = self.__select_committed_bss_ids()

        # Start sniffing on all sniffer interfaces
        print "{0} -> Sniffing is done on interfaces: {1}.".format(self.name, sniffer_interfaces)
        while not self.name.endswith("--"):
            try:
                sleep(self.__CPU_CYCLE_TIME)

                for sniffer_interface in sniffer_interfaces:
                    sniff(iface=sniffer_interface, count=1, prn=self.__radio_tap_handler, timeout=1)

            except Scapy_Exception as exception:
                print "Scapy exception in thread '{0}': {1}".format(self.name, exception)

            except Exception as exception:
                print "Exception in thread '{0}': {1}".format(self.name, exception)

    def __grep_sniffer_interfaces(self):
        """
        Get all sniffer interfaces and return them in a list

        Requires: Unix
        """
        # ifconfig -s | cut -d " " -f1 | grep <interface>
        command = subprocess.Popen(["ifconfig", "-s"], stdout=subprocess.PIPE)
        command = subprocess.Popen(["cut", "-d", " ", "-f1"], stdin=command.stdout, stdout=subprocess.PIPE)
        command = subprocess.Popen(["grep", self.__INTERFACE_STARTS_WITH], stdin=command.stdout, stdout=subprocess.PIPE)

        (std_out_data, std_error_data) = command.communicate()
        if std_error_data is None:
            sniffer_interfaces = std_out_data.split()
            print "{0} -> Detected sniffer interfaces: {1}".format(self.name, sniffer_interfaces)
            return sniffer_interfaces
        else:
            print "{0} -> Error while detecting sniffer interfaces: {1}".format(self.name, std_error_data)
            return list()

    def __set_monitor_mode_for_interface(self, interface):
        """
        Set all sniffer interfaces from the list into monitor mode

        Requires: Unix
        """

        # Force interface to be an sniffer interface
        if not isinstance(interface, str):
            print "{0} -> Not an sniffer interface string: {1}".format(self.name, interface)
            return False
        if not interface.startswith(Sniffer.__INTERFACE_STARTS_WITH):
            print "{0} -> Not an sniffer interface: {1}".format(self.name, interface)
            return False

        # ifconfig <interface> down
        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", interface, "down"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing interface '{1}' down: {2}" \
                .format(self.name, interface, std_error_data)
            return False

        # iwconfig <interface> mode Monitor
        (std_out_data, std_error_data) = subprocess.Popen(["iwconfig", interface, "mode", "Monitor"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while setting interface '{1}' in monitor mode: {2}" \
                .format(self.name, interface, std_error_data)
            return False

        # ifconfig <interface> up
        (std_out_data, std_error_data) = subprocess.Popen(["ifconfig", interface, "up"]).communicate()
        if std_error_data is not None:
            print "{0} -> Error while bringing interface '{1}' back up: {2}" \
                .format(self.name, interface, std_error_data)
            return False

        print "{0} -> Interface '{1}' configured succesfully.".format(self.name, interface)
        return True

    def __select_committed_bss_ids(self):
        """
        Select the BSS IDS from the database to prevent any double entries

        Requires: PostgreSQL database
        """
        connection = None
        cursor = None

        try:
            connection = psycopg2.connect(self.__CONNECTION_STRING)
            cursor = connection.cursor()

            cursor.execute("SELECT DISTINCT(bss_id) FROM dot11;")
            bss_ids = cursor.fetchall()
            if bss_ids is None:
                print "{0} -> No existing BSS IDs.".format(self.name)
                return list()

            bss_ids = [bss_id[0] for bss_id in bss_ids]
            return bss_ids
        except Exception as exception:
            print "Exception in thread '{0}': {1}".format(self.name, exception)
            return list()
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def __radio_tap_handler(self, radio_tap):
        """
        Dissects and pushes data from Radiotap packets to the Database class
        """

        # Force packet to be RadioTap
        if not isinstance(radio_tap, RadioTap):
            print "{0} -> Filtered '{1}' packet!".format(self.name, type(radio_tap).__name__)
            return

        # Force RadioTap's payload to be Dot11
        dot11 = radio_tap.payload
        if not isinstance(dot11, Dot11):
            print "{0} -> Filtered '{1}' layer!".format(self.name, type(dot11).__name__)
            return

        # Force Dot11's payload to be a Dot11 subtype
        dot11_subtype = dot11.payload
        dot11_subtype_name = type(dot11_subtype).__name__
        if not isinstance(dot11_subtype, (
                Dot11AssoReq, Dot11AssoResp, Dot11ReassoReq, Dot11ReassoResp, Dot11ProbeReq, Dot11ProbeResp,
                Dot11Beacon, Dot11ATIM, Dot11Disas, Dot11Auth, Dot11Deauth, Dot11WEP)):
            print "{0} -> Filtered '{1}' Dot11 subtype!".format(self.name, dot11_subtype_name)
            return

        # !!Currently only supports Dot11Beacon!!
        if not isinstance(dot11_subtype, Dot11Beacon):
            print "{0} -> Filtered '{1}' Dot11 subtype!".format(self.name, dot11_subtype_name)
            return

        # Check whether BSS ID has been committed before
        bss_id = dot11.fields['addr3']
        if bss_id in self.__committed_bss_ids:
            if bss_id not in self.__notified_duplicate_bss_ids:
                print "{0} -> Filtered duplicate BSS ID '{1}'!".format(self.name, bss_id)
                self.__notified_duplicate_bss_ids.append(bss_id)
            return

        # Loop trough Dot11 subtype's payload until it is NoPayload
        dot11_elts = list()
        dot11_elt = dot11_subtype.payload
        while not isinstance(dot11_elt, NoPayload):
            # Force Dot11 subtype's payload to be a Dot11Elt
            if not isinstance(dot11_elt, Dot11Elt):
                print "{0} -> Filtered '{1}' element!".format(self.name, type(dot11_elt).__name__)
                continue

            dot11_elts.append(dot11_elt)
            dot11_elt = dot11_elt.payload

        connection = None
        cursor = None

        try:
            # Set up connection
            connection = psycopg2.connect(self.__CONNECTION_STRING)
            cursor = connection.cursor()

            # Prepare query and parameters for RadioTap packet
            radio_tap_query = """
                INSERT INTO radio_tap(revision, pad, length, present_flags)
                VALUES({0}, {1}, {2}, {3})
                RETURNING pointer_radio_tap;
                """\
                .format("%(version)s", "%(pad)s", "%(len)s", "%(present)s")\
                .replace("  ", "")
            radio_tap_parameters = self.fix_str_dict(radio_tap.sprintf("%RadioTap.fields%"))

            # Execute and save the returning pointer
            cursor.execute(radio_tap_query, radio_tap_parameters)
            radio_tap_pointer = cursor.fetchone()[0]

            # Prepare query and parameters for Dot11 payload
            dot11_query = """
                INSERT INTO dot11(pointer_radio_tap, version, type, subtype, frame_control_field,
                address1, address2, address3, address4, bss_id)
                VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})
                RETURNING pointer_dot11;
                """\
                .format("%(pointer)s", "%(proto)s", "%(type)s", "%(subtype)s", "%(FCfield)s",
                        "%(addr1)s", "%(addr2)s", "%(addr3)s", "%(addr4)s", "%(bss_id)s")\
                .replace("  ", "")
            dot11_parameters = self.fix_str_dict(dot11.sprintf("%Dot11.fields%"))
            dot11_parameters['pointer'] = radio_tap_pointer
            dot11_parameters['bss_id'] = bss_id

            # Execute and save the returning pointer
            cursor.execute(dot11_query, dot11_parameters)
            dot11_pointer = cursor.fetchone()[0]

            # Prepare query and parameters for Dot11Beacon payload
            dot11_beacon_query = """
                INSERT INTO dot11_beacon(pointer_dot11, timestamp, beacon_interval, capabilities_information)
                VALUES({0}, {1}, {2}, {3});
                """\
                .format("%(pointer)s", "%(timestamp)s", "%(beacon_interval)s", "%(cap)s",)\
                .replace("  ", "")
            dot11_beacon_parameters = self.fix_str_dict(dot11_subtype.sprintf("%{0}.fields%".format(dot11_subtype_name)))
            dot11_beacon_parameters['pointer'] = dot11_pointer

            # Execute
            cursor.execute(dot11_beacon_query, dot11_beacon_parameters)

            # Loop trough Dot11Elt list
            for dot11_elt in dot11_elts:
                # Prepare query and parameters for Dot11Elt payload
                dot11_elt_query = """
                    INSERT INTO dot11_elt(pointer_dot11, number, length, info)
                    VALUES({0}, {1}, {2}, {3});
                    """ \
                    .format("%(pointer)s", "%(ID)s", "%(len)s", "%(info)s", ) \
                    .replace("  ", "")
                dot11_elt_parameters = self.fix_str_dict(dot11_elt.sprintf("%Dot11Elt.fields%"))
                dot11_elt_parameters['pointer'] = dot11_pointer

                # Execute
                cursor.execute(dot11_elt_query, dot11_elt_parameters)

            # Commit packet
            connection.commit()
            self.__committed_bss_ids.append(bss_id)
            print "{0} -> Added packet for BSS ID: '{1}'!".format(self.name, bss_id)
        except Exception as exception:
            print "Exception in thread '{0}': {1}".format(self.name, exception)

            # Rollback on ANY exception
            connection.rollback()
        finally:
            # Close the connections
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    def fix_str_dict(self, str_of_dict):
        # Turn type str into type dict
        dict_of_str = literal_eval(str_of_dict)

        for key, value in dict_of_str.iteritems():
            # Turn timestamp into datetime
            if isinstance(value, long) and key == "timestamp":
                dict_of_str[key] = self.long_to_timestamp(value)

            # Turn long into bitwise string
            elif isinstance(value, long) and key in self.__BITWISE_LENGTHS:
                dict_of_str[key] = self.long_to_bitwise(value, self.__BITWISE_LENGTHS[key])

            # Turn empty MAC addresses into zero filled MAC addresses
            elif str.startswith(key, 'addr'):
                dict_of_str[key] = value if value is not None else '00' + (':00' * 5)

            # Escape bytes
            elif isinstance(value, bytes):
                dict_of_str[key] = repr(value)

        return dict_of_str

    def long_to_bitwise(self, number, length):
        """
        Create a bitwise string from a long type
        """
        if not isinstance(number, long):
            return None

        return "{0:b}".format(number).zfill(length)

    def long_to_timestamp(self, number):
        """
        Create a timestamp from a long type
        """
        if not isinstance(number, long):
            return None

        try:
            timestamp = datetime.fromtimestamp(number)
        except:
            timestamp = datetime.now()

        return timestamp
