from Movement.CarControl import CarControl
from threading import Thread
from Enums import MovementType, TurnModeType
from pubsub import pub
import sys


class Keyboard(Thread):
    __CPU_CYCLE_TIME = 0.05  # 50 ms
    __CAR_SPEED = 50

    __carMovement = None
    __isRunning = False

    __turnMode = TurnModeType.Turning
    __moveType = MovementType.Idle

    # Event identifiers used for event listeners.
    EVENT_ON_MOVETYPE_CHANGED = "OnMoveTypeChanged"

    def __init__(self):
        Thread.__init__(self)

        # Initialise car hardware library.
        self.__carMovement = CarControl()

    def join(self, timeout=None):
        self.__shutdown_controller()
        super(Keyboard)

    def run(self):

        self.__isRunning = True

        self.__set_move_type(MovementType.Idle)
        
        while self.__isRunning:
            try:
                key = sys.stdin.read(3)

                if key == "":
                    continue

                if key == "\x1b[A":  # Up arrow key
                    self.__set_move_type(MovementType.Forward)
                elif key == "\x1b[B":  # Down arrow key
                    self.__set_move_type(MovementType.Reverse)
                elif key == "\x1b[C":  # Right arrow key
                    if self.__turnMode == TurnModeType.Turning:
                        self.__set_move_type(MovementType.Turn_Right)
                    else:
                        self.__set_move_type(MovementType.Spin_Right)
                elif key == "\x1b[D":  # Left arrow key
                    if self.__turnMode == TurnModeType.Turning:
                        self.__set_move_type(MovementType.Turn_Left)
                    else:
                        self.__set_move_type(MovementType.Spin_Left)
                elif key == "m" or key == "M":  # m or M key
                    self.__switch_turn_mode()
                else:
                    self.__set_move_type(MovementType.Idle)

                print "Keyboard input : " + str(key)

            except EOFError:
                print "Program has read input from a file! -- Probably in testing mode, shutting down module!"
                self.__shutdown_controller()
            except IOError:
                self.__set_move_type(MovementType.Idle)
            except KeyboardInterrupt:
                self.__shutdown_controller()

    def __set_move_type(self, new_move_type):
        if self.__moveType == new_move_type:
            return

        self.__moveType = new_move_type
        print "Move type changed to " + str(new_move_type)
        pub.sendMessage(self.EVENT_ON_MOVETYPE_CHANGED, move_type=self.__moveType)

    def __switch_turn_mode(self):
        self.__turnMode = not self.__turnMode
        if self.__turnMode == TurnModeType.Turning:
            print "Movement -> Changed to turn mode"
        else:
            print "Movement -> Changed to spin mode"

    def __shutdown_controller(self):
        if not self.__isRunning:
            return

        print "Shutting down keyboard controller..."
        self.__isRunning = False
