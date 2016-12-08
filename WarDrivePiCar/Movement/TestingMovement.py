from Movement import initio
from time import sleep

try:
    # Start the controller
    initio.init()
    # Block the main thread
    while True:
        sleep(0.1)
        initio.forward(50)
except KeyboardInterrupt:
    # On keyboard interrupt cleanup GPIO pins and shutdown initio library functions
    initio.cleanup()

