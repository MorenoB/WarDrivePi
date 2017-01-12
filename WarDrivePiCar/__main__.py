import os
import sys
import pydevd

from program import Program
from sys_argv import SysArgv


if __name__ == "__main__":
    print "\nPython {0}\n".format(sys.version)

    sys_argv = SysArgv()

    if not sys_argv.validate():
        sys_argv.print_argv()
        print "Invalid arguments! Exited."
        exit()

    if "trace" in sys_argv.items:
        pydevd.settrace(
            host=sys_argv.items['trace'],
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
            patch_multiprocessing=True
        )

        if not pydevd.connected:
            print "Couldn't not reach REMOTE DEBUGGER on '{0}'!".format(sys_argv.items['trace'])
            os.system("ping -c 1 {0}".format(sys_argv.items['trace']))

    # Boot up program
    program = Program()
    program.start()

    if pydevd.connected:
        pydevd.stoptrace()
