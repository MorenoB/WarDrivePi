from WarDrivePiCar.Controller.Controller import Controller
from time import sleep

def main():
    controller = Controller()

    try:
        # Start the controller
        controller.start()

        # Block the main thread
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        # On keyboard interrupt stop the traffic controller
        controller.stop()

pass


if __name__ == "__main__":
    main()
