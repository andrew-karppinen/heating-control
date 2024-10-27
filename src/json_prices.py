 
from datetime import date,datetime,timedelta
import requests
import os
import json
import pytz
from tzlocal import  get_localzone


def muunna_aikaleima(aikaleima_str):
    # Määritä aikaformaatti
    aikaformaatti = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Käytä strptime-funktiota parsimiseen
    try:
        aikaleima_dt = datetime.strptime(aikaleima_str, aikaformaatti)
        return aikaleima_dt
    except ValueError as e:
        print(f"Virhe: {e}")
        return None


def has_next_day_prices(data):
    '''
    Tutkii hintatiedot ja jos sieltä löytyy seuraavan päivän hintatiedot palauttaa True muuten False
    '''        

    prices = data.get("prices", [])
    if not prices:
        return False

    # Get the current date
    current_date = datetime.now().date()

    # Define the upcoming day
    upcoming_day = current_date + timedelta(days=1)

    # Create a set of all hours for the upcoming day
    all_hours = {datetime.combine(upcoming_day, datetime.min.time()) + timedelta(hours=i) for i in range(24)}

    # Collect the hours present in the price data for the upcoming day
    present_hours = set()
    for price_info in prices:
        start_date = datetime.fromisoformat(price_info["startDate"][:-1]) #format str to datetime object
        if start_date.date() == upcoming_day:
            present_hours.add(start_date)

    # Check if all hours are present
    return all_hours == present_hours

def GetCurrentPrice(jsondata)->float:
    '''
    lukee json datasta nykyisen tunnin hinnan ja palauttaa sen
    jos sitä ei löydy palauttaa None
    '''


    prices = jsondata["prices"]  # read settings


    for i in prices:

        current_time = datetime.now()


        if muunna_aikaleima(i["startDate"]).day == current_time.day and muunna_aikaleima(i["startDate"]).hour == current_time.hour:
            price = i["price"]
            return price

    return None




def GetCurrentDayPrices(jsondata)->list:

    prices = jsondata["prices"]  # read settings


    today_prices = []
    for i in prices:

        if muunna_aikaleima(i["startDate"]).day == datetime.now().day:
            today_prices.append(i["price"])


    return today_prices


def convert_to_local_time(json_data:dict):
    def muunna_aika(aika):
        # Muunna merkkijono datetime-objektiksi
        utc_aika = datetime.fromisoformat(aika[:-1])

        #Hanki tietokoneen paikallinen aikavyöhyke
        paikallinen_aikavyohyke = get_localzone()

        #Muunna UTC-aika paikalliseksi ajaksi
        paikallinen_aika = utc_aika.replace(tzinfo=pytz.utc).astimezone(paikallinen_aikavyohyke)

        #Palauta paikallinen aika merkkijonona
        return paikallinen_aika.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    # Kopioidaan syötteenä saatu data, jotta alkuperäistä dataa ei muokata
    muokattu_data = json_data

    for price_entry in muokattu_data['prices']:
        price_entry['startDate'] = muunna_aika(price_entry['startDate'])
        price_entry['endDate'] = muunna_aika(price_entry['endDate'])

    return muokattu_data
def Write48hPricesToJSON() -> bool:

    '''
    Hakee 42 tunin hintatiedot netistä ja kirjoittaa ne json tiedostoon

    Jos kello yli 16 ja tämän päivän hintatietoja ei ole haettu, haetaan uudet hintatiedot ja nimetään ne tänää päivän mukaan
    tässä tapauksessa varmistetaan että uudet hintatiedot todella sisältävät seuraavan päivän hintatiedot, jos ei palautetaan False eli virhe

    jos kello alle 16 ja tämän eikä eilisen päivän hintatietoja haettu haetaan uudet hintatiedot ja nimetään ne eilisen päivän mukaan

    tiedot tallennetaan json tiedostoon jotka nimetään päivien mukaan, tästä saadaan myös tieto minkä päivän hinnat on jo olemassa jne
    
    jos hintojen haku esim internetyhteyden takia ei toimi palauttaa False, muuten True
    
    
    muuttaa ajan utc ajasta suomen aikaan(2 tuntia vähemmän)
    '''


    def Write(name_yesterday:bool):
        # write 48h prices to json file
        
        try:
            api_endpoint = f"https://api.porssisahko.net/v1/latest-prices.json"  # api endpoint
            json_data = requests.get(api_endpoint).json()  # get json

            json_data = convert_to_local_time(json_data) #convert times to Finnish time zone
            json_object = json.dumps(json_data, indent=4)  # json to str
        except Exception as a:
            print(a)
            return False


        
        if name_yesterday == False:
            with open(f"data/prices/{today}.json", "w") as outfile:
                outfile.write(json_object)
        else:
            with open(f"data/prices/{yesterday}.json", "w") as outfile:
                outfile.write(json_object)


    # get current date
    today = str(date.today())  # tämä päivä
    yesterday = str(date.today() - timedelta(days=1))  # eilinen päivä
    hour = datetime.now().hour  # nykyinen tunti

    if hour > 16:  # kello yli 16
        if os.path.isfile(f"data/prices/{today}.json") == False:  # if json file is not already in exist
            if Write(name_yesterday=False) == False:
                return False
            else:
                return True
        else: #json file is allready in exist, check if it has next day prices
            with open(f"data/prices/{today}.json", "r") as outfile:
                json_data = json.loads(outfile.read()) #read json file to dict
            if has_next_day_prices(json_data) == False:
                if Write(name_yesterday=False) == False:
                    return False
                else:
                    with open(f"data/prices/{today}.json", "r") as outfile:
                        json_data = json.loads(outfile.read())  # read json file to dict
                    if has_next_day_prices(json_data) == False:
                        return False
                    else:
                        return True
            else:
                return True

    else:  # kello alle 16
        if os.path.isfile(f"data/prices/{yesterday}.json") == False:  # if json file is not already in exist
            if os.path.isfile(f"data/prices/{today}.json") == False:  # if json file is not already in exist

                if Write(name_yesterday=True) == False:
                    return False
                else:
                    return True

    return True

if __name__ == "__main__":

    file = open("data/prices/2024-10-26.json", "r")
    json_data = file.read()
    file.close()
    json_data = json.loads(json_data)

    print(has_next_day_prices(json_data))

    #print(GetCurrentDayPrices(json_data))
    #print(GetCurrentPrice(json_data))
    #print(Write48hPricesToJSON())
