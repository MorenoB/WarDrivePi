import os
import sys
import pydevd
import SysArgv
import Main

if __name__ == "__main__":
    print "\nPython {0}\n".format(sys.version)

    SysArgv = SysArgv.SysArgv()

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

    # Boot up program
    program = Main.Main()
    program.start()

    if pydevd.connected:
        pydevd.stoptrace()
