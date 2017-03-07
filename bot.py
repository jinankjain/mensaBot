#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import json
import locale
import calendar
import datetime
import time
import pytz

# 1 is lunch, 0 is dinner
now = datetime.datetime.now(pytz.timezone('Europe/Zurich'))
index = (int(now.strftime("%w"))+6)%7
hour = now.strftime("%H")

ETH_MENSA_NOMEAL_STR = 'No lunch menu today.'
FDATE = '{}.{}.{}'.format(now.day, now.strftime("%m"), now.year)

def eth_parse_table(table):
    menu = ""
    for row in table[0].findAll('tr')[0:]:
        col = row.findAll('td')
        j = 0
        for c in col:
            if(j == 0 or j == 1):
                for b in c.findAll("br"):
                    b.replaceWith(" ")
                menu += c.text.replace("Show details", "")
                menu += "\n"
            j += 1
    return menu + "\n"
    

def parse_eth_menu(lunch_or_dinner):
    r = requests.get("https://www.ethz.ch/en/campus/gastronomie/menueplaene/offerDay.html?language=en&id=12&date={}-{}-{}".format(now.year, now.strftime("%m"), now.strftime("%d")))
    if ETH_MENSA_NOMEAL_STR in r.text:
        return "No ETH menu available for this day!"

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.findAll('table')
    menu = ""
    menu += "*Expensive mensa:* \n \n"
    if lunch_or_dinner == 1:
        menu += "*Lunch:* \n"
    else:
        menu += "*Dinner:* \n"

    menu += eth_parse_table(table)

    return menu

def parse_uzh_menu(lunch_or_dinner):
    locale.setlocale(locale.LC_ALL, 'de_CH.utf-8')
    curr_day = str(calendar.day_name[index]).lower()

    menu = ""
    menu += "*Cheap mensa:*" + "\n\n"
    if lunch_or_dinner == 1:
        menu += "*Lunch:*" + "\n"
        r = requests.get("http://www.mensa.uzh.ch/de/menueplaene/zentrum-mensa/{}.html".format(curr_day))

        if not FDATE in r.text:
            return "No UZH menu available for this day!"

        soup = BeautifulSoup(r.text, 'html.parser')
        menu_div = soup.findAll("div", { "class" : "text-basics" })
        menu_div.pop(0)

        for m in menu_div:
            heading =  m.findAll('div')[0].findAll('h3')
            para = m.findAll('div')[0].findAll('p')
            for i in range(0, len(heading)-1):
                menu+=str(heading[i].text).split("|")[0]
                menu+="\n"
                menu+=str(para[i].text)
                menu+="\n"
    else:
        menu += "\n*Dinner:* \n"
        r = requests.get("http://www.mensa.uzh.ch/de/menueplaene/zentrum-mercato-abend/{}.html".format(curr_day))
        soup = BeautifulSoup(r.text, 'html.parser')
        menu_div = soup.findAll("div", { "class" : "text-basics" })
        menu_div.pop(0)

        for m in menu_div:
            heading =  m.findAll('div')[0].findAll('h3')
            para = m.findAll('div')[0].findAll('p')
            for i in range(0, len(heading)-1):
                menu+=str(heading[i].text).split("|")[0]
                menu+="\n"
                menu+=str(para[i].text)
                menu+="\n"

    return menu

def main():
    if int(hour) > 12:
        lunch_or_dinner = 0
    else:
        lunch_or_dinner = 1

    menu = ""
    menu += parse_eth_menu(lunch_or_dinner)
    menu += parse_uzh_menu(lunch_or_dinner)
    
    print(menu)
    return

    slack_data = {'channel':'#vippartyroom', 'username': 'mensamenu', 'text': menu}
    url = 'https://hooks.slack.com/services/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'
    r = requests.post(url, data = json.dumps(slack_data))

if __name__ == "__main__":
    main()

