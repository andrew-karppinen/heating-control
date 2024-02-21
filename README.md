
#  Lämmityksenohjaus sovellus raspberry piille


### Lataa uusin versio: [releases tab](https://github.com/andrew-karppinen/heating-control/releases/latest)


### Asenna python kirjastot:

> pip install pysimplegui

RPi.GPIO kirjastoa ei ole jo asennettu asenna se:
https://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/



### Rele

Jos haluat ohjata relettä kytke se raspberry piin pinniin GPIO 27


### Lämpötila sensori

Halutessi voit kytkeä dht11 tai dht22 pinniin  GPIO 4
Tällöin tarvitset pythoniin myös Adafruit_DHT kirjaston

Lisätietoa dht11/22 asentamisesta:
https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/


### Käynnistä sovellus:
> python3 intrerface.py