from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import json
import locale
import calendar
import datetime
import time
import pytz

sched = BlockingScheduler()
tz = pytz.timezone('Europe/Zurich')
now = datetime.datetime.now(tz)
index = (int(now.strftime("%w"))+6)%7

ETH_MENSA_NOMEAL_STR = 'No lunch menu today.'
FDATE = '{}.{}.{}'.format(now.day, now.strftime("%m"), now.year)

def parse_eth_menu(lunch_or_dinner):
    r = requests.get("https://www.ethz.ch/en/campus/gastronomie/menueplaene/offerDay.html?language=en&id=12&date={}-{}-{}".format(now.year, now.strftime("%m"), now.day))

    if ETH_MENSA_NOMEAL_STR in r.text:
        return "No ETH menu available for this day!"

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.findAll('table')

    menu = "*Expensive mensa:* \n \n"
    if lunch_or_dinner == 1:
        menu += "*Lunch:* \n"
        for row in t[0].findAll('tr')[0:]:
            col = row.findAll('td')
            j = 0
            for c in col:
                if(j == 0 or j == 1):
                    menu+=c.text
                    menu+="\n"
                j+=1
        menu+="\n"
    else:
        menu += "*Dinner:* \n"
        for row in t[1].findAll('tr')[0:]:
            col = row.findAll('td')
            j = 0
            for c in col:
                if(j == 0 or j == 1):
                    menu+=c.text
                    menu+="\n"
                j+=1
        menu+="\n"


def parse_uzh_menu(lunch_or_dinner):
    locale.setlocale(locale.LC_ALL, 'de_CH.utf-8')
    curr_day = str(calendar.day_name[index]).lower()

    menu = ""
    menu += "*Cheap mensa:* \n \n"
    if lunch_or_dinner == 1:
        menu += "*Lunch:* \n"
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

# lunch_or_dinner = 1 -> Lunch else Dinner
def corn_job(lunch_or_dinner):
    print(lunch_or_dinner)
    eth_menu = parse_eth_menu(lunch_or_dinner)
    uzh_menu = parse_uzh_menu(lunch_or_dinner)
    print(eth_menu + "\n" + uzh_menu)
    menu = eth_menu + "\n\n" + uzh_menu
    slack_data = {'channel':'#vippartyroom', 'username': 'mensamenu', 'text': menu}
    url = 'https://hooks.slack.com/services/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'
    r = requests.post(url, data = json.dumps(slack_data))
    print(r.text)
    if lunch_or_dinner == 0:
        sched.add_job(corn_job, 'date', run_date=datetime.datetime(int(now.year), int(now.strftime("%m")), int(now.day), 11, 00, 0)+datetime.timedelta(days=1), args=[1])
    else:
        sched.add_job(corn_job, 'date', run_date=datetime.datetime(int(now.year), int(now.strftime("%m")), int(now.day), 17, 00, 0), args=[0])

today11am = now.replace(hour=11, minute=0, second=0, microsecond=0)
today5pm = now.replace(hour=17, minute=0, second=0, microsecond=0)
today12am = now.replace(hour=23, minute=59, second=59, microsecond=59)

if now > today11am and now < today5pm:
    sched.add_job(corn_job, 'date', run_date=datetime.datetime(int(now.year), int(now.strftime("%m")), int(now.day), 17, 00, 0), args=[0])
elif now > today5pm and now < today12am:
    sched.add_job(corn_job, 'date', run_date=datetime.datetime(int(now.year), int(now.strftime("%m")), int(now.day), 11, 00, 0)+datetime.timedelta(days=1), args=[1])
else:
    sched.add_job(corn_job, 'date', run_date=datetime.datetime(int(now.year), int(now.strftime("%m")), int(now.day), 11, 00, 0), args=[1])

sched.start()
