import RPi.GPIO as GPIO
import time




def RelayControl(on:bool):

    '''
    Control the state of a relay connected to a Raspberry Pi GPIO pin.

    Args:
    on (bool): True to turn the relay on, False to turn it off.
    '''

    gpio_pin = 27
    GPIO.setmode(GPIO.BCM)



    if on == True:
        GPIO.setup(gpio_pin, GPIO.OUT) #turn on gpio


    elif on == False:

        GPIO.setup(gpio_pin,GPIO.IN) #turn off gpio





if __name__ == "__main__":
    
    RelayControl(False)

  