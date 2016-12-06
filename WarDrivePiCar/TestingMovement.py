from WarDrivePiCar.Movement import initio
from time import sleep

try:
    # Start the controller
    movement = initio()
    movement.init()
    # Block the main thread
    while True:
        sleep(0.1)
        movement.forward(1)
except KeyboardInterrupt:
    # On keyboard interrupt stop the traffic controller
    movement.cleanup()

