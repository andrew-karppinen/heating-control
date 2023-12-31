 
from datetime import date,datetime,timedelta
import requests
import os
import json




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



def GetCurrentPrice(jsondata)->float:
    '''
    lukee json datasta nykyisen tunnin hinnan ja palauttaa sen
    jos sitä ei löydy palauttaa None
    '''


    prices = jsondata["prices"]  # read settings


    for i in prices:

        if muunna_aikaleima(i["startDate"]).day == datetime.now().day and muunna_aikaleima(i["startDate"]).hour == datetime.now().hour-2:
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


def Write48hPricesToJSON() -> bool:

    '''
    Hakee 42 tunin hintatiedot netistä ja kirjoittaa ne json tiedostoon

    Jos kello yli 16 ja tämän päivän hintatietoja ei ole haettu, haetaan uudet hintatiedot ja nimetään ne tänää päivän mukaan

    jos kello alle 16 ja tämän eikä eilisen päivän hintatietoja haettu haetaan uudet hintatiedot ja nimetään ne eilisen päivän mukaan

    tiedot tallennetaan json tiedostoon jotka nimetään päivien mukaan, tästä saadaan myös tieto minkä päivän hinnat on jo olemassa jne
    
    jos hintojen haku esim internetyhteyden takia ei toimi palauttaa False, muuten Ttue
    '''


    def Write(name_yesterday:bool):
        # write 48h prices to json file
        
        try:
            api_endpoint = f"https://api.porssisahko.net/v1/latest-prices.json"  # api endpoint
            json_data = requests.get(api_endpoint).json()  # get json

            json_object = json.dumps(json_data, indent=4)  # json to str
        except:
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



    else:  # kello alle 16
        if os.path.isfile(f"data/prices/{yesterday}.json") == False:  # if json file is not already in exist
            if os.path.isfile(f"data/prices/{today}.json") == False:  # if json file is not already in exist

                if Write(name_yesterday=True) == False:
                    return False
                else:
                    return True

    return True

if __name__ == "__main__":

    #file = open("data/prices/2023-12-30.json", "r")
    #json_data = file.read()
    #file.close()
    #json_data = json.loads(json_data)


    #print(GetCurrentDayPrices(json_data))
    #print(GetCurrentPrice(json_data))
    print(Write48hPricesToJSON())