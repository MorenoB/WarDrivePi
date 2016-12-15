import os
import sys

from threading import Thread
from Controller.Controller import Controller
from Sniffer.Sniffer import Sniffer

from time import sleep

import pydevd

__CYCLE_TIME = 0.1  # 100 ms


class SysArgv:

    def __init__(self):
        pass

    items = dict()

    @staticmethod
    def print_argv():
        print 'Number of arguments: {0} arguments.'.format(len(sys.argv))
        print 'Argument list: {0}'.format(str(sys.argv))

    @staticmethod
    def validate():
        index = 1
        while index < len(sys.argv):

            if sys.argv[index] == "-m" or sys.argv[index] == "--module":
                index += 1
                if index < len(sys.argv):
                    SysArgv.items['module'] = sys.argv[index]
                else:
                    return False

            elif sys.argv[index] == "-t" or sys.argv[index] == "--trace":
                index += 1
                if index < len(sys.argv):
                    SysArgv.items['trace'] = sys.argv[index]
                else:
                    return False

            elif sys.argv[index] == "-v" or sys.argv[index] == "--verbose":
                SysArgv.items['verbose'] = True

            else:
                print "Argument not recognized '{0}'.".format(sys.argv[index])
                return False

            index += 1

        return True


def main():

    print "Application started... {0}".format("(w/ REMOTE DEBUGGING [{0}])".format(SysArgv.items['trace'])
                                              if pydevd.connected else str())

    # Classes should inherit from a Thread and need to join on an KeyboardInterrupt
    __threads = [
        Controller(),
        Sniffer()
    ]

    __start_threads(__threads)

    while True:
        try:
            sleep(__CYCLE_TIME)

        except KeyboardInterrupt:
            print
            __join_threads(__threads)
            print "Application stopped by KeyboardInterrupt."
            return

        except Exception as exception:
            print "Exception in 'main': {0}".format(exception)


def __start_threads(threads):
    for thread_instance in threads:
        if not isinstance(thread_instance, Thread):
            continue

        thread_instance.setName(type(thread_instance).__name__)

        print "Thread '{0}' starting...".format(thread_instance.getName())
        if not thread_instance.isAlive():
            thread_instance.start()
        print "Thread '{0}' started.".format(thread_instance.getName())


def __join_threads(threads):
    for thread_instance in threads:
        if not isinstance(thread_instance, Thread):
            continue

        thread_instance_name = thread_instance.getName()
        thread_instance.setName(thread_instance_name + "--")

        print "Thread '{0}' joining...".format(thread_instance_name)
        if thread_instance.isAlive():
            thread_instance.join()
        print "Thread '{0}' joined.".format(thread_instance_name)

if __name__ == "__main__":
    print "\nPython {0}\n".format(sys.version)

    if not SysArgv.validate():
        SysArgv.print_argv()
        print "Invalid arguments! Exited."
        exit()

    if "trace" in SysArgv.items:
        pydevd.settrace(
            host=SysArgv.items['trace'],
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
            patch_multiprocessing=True
        )

        if not pydevd.connected:
            print "Couldn't not reach REMOTE DEBUGGER on '{0}'!".format(SysArgv.items['trace'])
            os.system("ping -c 1 {0}".format(SysArgv.items['trace']))

    main()

    if pydevd.connected:
        pydevd.stoptrace()
