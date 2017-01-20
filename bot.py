from bs4 import BeautifulSoup
import requests
import json
import locale
import calendar
import datetime
import time
import pytz

tz = pytz.timezone('Europe/Zurich')
now = datetime.datetime.now(tz)
index = (int(now.strftime("%w"))+6)%7

r = requests.get("https://www.ethz.ch/en/campus/gastronomie/menueplaene/offerDay.html?language=en&id=12&date={}-{}-{}".format(now.year, now.strftime("%m"), now.day))
soup = BeautifulSoup(r.text, 'html.parser')
table = soup.findAll('table')

menu = "*Expensive mensa:* \n \n"
i = 0
for t in table:
    if i == 0:
        menu += "*Lunch:* \n"
        i += 1
    else:
        menu += "*Dinner:* \n"
    for row in t.findAll('tr')[0:]:
        col = row.findAll('td')
        j = 0
        for c in col:
            if(j == 0 or j == 1):
                menu+=c.text
                menu+="\n"
            j+=1
    menu+="\n"

locale.setlocale(locale.LC_ALL, 'de_DE')
curr_day = str(calendar.day_name[index]).lower()

menu += "\n"
menu += "*Cheap mensa:* \n \n"
print(curr_day)
menu += "*Lunch:* \n"
r = requests.get("http://www.mensa.uzh.ch/de/menueplaene/zentrum-mensa/{}.html".format(curr_day))
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

print(menu)

# slack_data = {'channel':'#vippartyroom', 'username': 'mensamenu', 'text': menu}
# url = 'https://hooks.slack.com/services/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'

# r = requests.post(url, data = json.dumps(slack_data))
# print(r.text)