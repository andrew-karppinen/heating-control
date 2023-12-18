import json
from datetime import datetime


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



def GetCurrentDayPrices(jsondata):



    prices = jsondata["prices"]  # read settings


    today_prices = []
    for i in prices:

        if muunna_aikaleima(i["startDate"]).day == datetime.now().day or muunna_aikaleima(i["endDate"]).day == datetime.now().day:
            today_prices.append(i["price"])


    return today_prices


if __name__ == "__main__":
    print(GetCurrentDayPrices("../2023-11-30.json"))

