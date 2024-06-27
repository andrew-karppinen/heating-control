import RPi.GPIO as GPIO

def RelayControl(on: bool):
    '''
    Control the state of a relay connected to a Raspberry Pi GPIO pin.

    Args:
    on (bool): True to turn the relay on, False to turn it off.
    '''



    gpio_pin = 6
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.OUT)

    if on:
        GPIO.output(gpio_pin, GPIO.HIGH)  # turn on relay
    else:
        GPIO.output(gpio_pin, GPIO.LOW)   # turn off relay

if __name__ == "__main__":
    try:
        RelayControl(False)
    finally:
        GPIO.cleanup()  # Clean up GPIO settings
