import RPi.GPIO as GPIO # always needed with RPi.GPIO  
from time import sleep  # pull in the sleep function from time module  
  
PIN_USED = 17
  
GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD numbering schemes. I use BCM  
  
GPIO.setup(PIN_USED, GPIO.OUT)# set pin output
  
red = GPIO.PWM(PIN_USED, 100)      # create object red for PWM on pin at 100 Hertz  
  
red.start(0)              # red off ( duty cycle is zero)  
  
pause_time = 0.02
  
try:  
    while True:  
        for i in range(0,101):      # 101 because it stops when it finishes 100  
            red.ChangeDutyCycle(i)  
            sleep(pause_time)  
        for i in range(100,-1,-1):      # from 100 to zero in steps of -1  
            red.ChangeDutyCycle(i)  
            sleep(pause_time)  
  
except KeyboardInterrupt:  
    red.stop()              # stop the red PWM output  
    GPIO.cleanup()          # clean up GPIO on CTRL+C exit  