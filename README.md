
#  Lämmityksenohjaus sovellus raspberry piille.

Ohjaa lämmitystä pörssisähkön hinnan mukaan.


<img width="644" height="518" alt="kuva" src="https://github.com/user-attachments/assets/04f83664-9c51-4d77-bac1-4ccde96f0687" />

<img width="644" height="518" alt="kuva" src="https://github.com/user-attachments/assets/b7a57473-f754-43f7-81d6-0af6db0d65bc" />



### Lataa uusin versio: [releases tab](https://github.com/andrew-karppinen/heating-control/releases/latest)


### Asenna python kirjastot:

> pip install tkinter

> pip install pytz

> pip install tzlocal

> pip install jsonschema 


RPi.GPIO kirjastoa ei ole jo asennettu asenna se:
https://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/



### Rele

Jos haluat ohjata relettä kytke se raspberry piin pinniin GPIO 6


### Lämpötila sensori

Halutessasi voit kytkeä dht11 tai dht22 pinniin  GPIO 5
Tällöin tarvitset pythoniin myös Adafruit_DHT kirjaston

Lisätietoa dht11/22 asentamisesta:
https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/


### Käynnistä sovellus:
> python3 interface_tkinter.py
