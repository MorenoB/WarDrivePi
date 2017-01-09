import sys


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
