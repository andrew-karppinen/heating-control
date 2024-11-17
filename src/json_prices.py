 
from datetime import date,datetime,timedelta
import requests
import os
import json
import pytz
from tzlocal import  get_localzone
from jsonschema import validate, ValidationError

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



def IsValid(json_data)->None:
    '''
    check json price data is valid
    causes ValidationError if json data is invalid
    :param json_data:
    '''

    schema = {
        "type": "object",
        "properties": {
            "prices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "price": {"type": "number"},
                        "startDate": {"type": "string", "format": "date-time"},
                        "endDate": {"type": "string", "format": "date-time"}
                    },
                    "required": ["price", "startDate", "endDate"]
                }
            }
        },
        "required": ["prices"]
    }

    validate(instance=json_data, schema=schema)




def ReadPrices()->dict:
    '''
    Read json data from file
    if json file is incorrect return False
    :return: json data as dict
    '''


    today = str(date.today())  # current day
    yesterday = str(date.today() - timedelta(days=1))  # yesterday

    if os.path.isfile(f"data/prices/{today}.json") == True:  # if today data is exist
        json_file_name = f"data/prices/{today}.json"
    elif os.path.isfile(f"data/prices/{yesterday}.json") == True:  # if yesterday data is exist
        json_file_name = f"data/prices/{yesterday}.json"
    else:
        return False

    try:
        file = open(json_file_name, "r")
        json_data = json.loads(file.read())
        file.close()

        IsValid(json_data) #check json data is valid

    except: #corrupted json file
        if Write48hPricesToJSON(overwrite=True) == False: # try to write prices to json
            return False
        prices = ReadPrices() #recursive call
        if prices != False:
            return prices
        else:
            return False

    return json_data


def has_next_day_prices(jsondata):
    '''
    Tutkii hintatiedot ja jos sieltä löytyy seuraavan päivän hintatiedot palauttaa True muuten False
    '''        

    prices = jsondata.get("prices", [])
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

        #hae tietokoneen paikallinen aikavyöhyke
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

def Write48hPricesToJSON(overwrite:bool=False) -> bool:

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
            json_data = requests.get(api_endpoint,timeout=5).json()  # get json

            IsValid(json_data)  # check json data is valid

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
        if os.path.isfile(f"data/prices/{today}.json") == False or overwrite == True:  # if json file is not already in exist
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
        if os.path.isfile(f"data/prices/{yesterday}.json") == False or overwrite == True:  # if json file is not already in exist
            if os.path.isfile(f"data/prices/{today}.json") == False or overwrite == True:  # if json file is not already in exist

                if Write(name_yesterday=True) == False:
                    return False
                else:
                    return True

    return True

if __name__ == "__main__":

    #file = open("data/prices/2024-11-17.json", "r")
    #json_data = file.read()
    #file.close()
    #json_data = json.loads(json_data)

    #print(IsValid(json_data))
    #print(has_next_day_prices(json_data))

    print(ReadPrices())

    #print(GetCurrentDayPrices(json_data))
    #print(GetCurrentPrice(json_data))
    #print(Write48hPricesToJSON())
