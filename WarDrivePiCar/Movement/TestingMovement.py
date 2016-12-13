import initio
from time import sleep

try:
    # Block the main thread
    while True:
        sleep(0.1)
        initio.forward(15)
except KeyboardInterrupt:
    # On keyboard interrupt cleanup GPIO pins and shutdown initio library functions
    initio.stop()

