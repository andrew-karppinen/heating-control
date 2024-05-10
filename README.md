
#  Lämmityksenohjaus sovellus raspberry piille.

Ohjaa lämmitystä pörssisähkön hinnan mukaan.

![Kuvakaappaus 2024-02-21 10-36-36](https://github.com/andrew-karppinen/heating-control/assets/99529988/ffc3d48f-85cc-4206-ae21-d91b45234194)


### Lataa uusin versio: [releases tab](https://github.com/andrew-karppinen/heating-control/releases/latest)


### Asenna python kirjastot:

> pip install tkinter

> pip install pytz

> pip install tzlocal


RPi.GPIO kirjastoa ei ole jo asennettu asenna se:
https://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/



### Rele

Jos haluat ohjata relettä kytke se raspberry piin pinniin GPIO 27


### Lämpötila sensori

Halutessasi voit kytkeä dht11 tai dht22 pinniin  GPIO 4
Tällöin tarvitset pythoniin myös Adafruit_DHT kirjaston

Lisätietoa dht11/22 asentamisesta:
https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/


### Käynnistä sovellus:
> python3 interface_tkinter.py
