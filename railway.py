import bs4
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from fuzzywuzzy import process
import pickle


class Railway:
    def __init__(self):
        self.stations = json.load(open(os.path.join(os.path.dirname(__file__), 'stations.json')))
        self.trains = json.load(open(os.path.join(os.path.dirname(__file__), 'trains.json')))

    def get_station_code(self, station):
        try:
            return self.stations[station.upper()]
        except KeyError:
            print(process.extractOne(station, self.stations.values()))
            return process.extractOne(station, self.stations.values())[0]

    def train_between_station(self, from_st, to_st, date):
        from_station = self.get_station_code(from_st).split(' - ')[1]
        to_station = self.get_station_code(to_st).split(' - ')[1]
        date_ = str(date).replace('-', '%2F')

        base_url = "https://www.railyatri.in/booking/trains-between-stations"

        param = {
            "from_code": from_station,
            "from_name": from_st.replace(' ', '+'),
            "journey_date": date_,
            "to_code": to_station,
            "to_name": to_st.replace(' ', '+'),
            "user_id": "-" + str(time.time()),
            "user_token": "140475"
        }

        r = requests.get(base_url, params=param)
        soup = BeautifulSoup(r.content, 'html5lib')
        trains = soup.find_all('tr', class_="tbs-main-row")

        info = []

        for train in trains:
            q = train.find('div', class_="col-md-8 left-panel no-pad")
            schedule = q.find_all('span')
            fares = q.find('div').find_all('a')

            data = {
                "train_number": train.attrs["data-number"],
                "train_name": train.attrs["data-name"],
                "runday": train.attrs["data-runday"],
                "from_station": train.attrs["data-from"],
                "to_station": train.attrs["data-to"],
                "arrival_time": schedule[1].text,
                "reach_time": schedule[4].text,
                "journey_time": schedule[5].text,
                # "ontime": schedule[6].text,
                "classes": [(e["data-coach"], e.div.find_all('p')[1].text, e["data-redirect_url"]) for e in fares]
            }
            req_info = (   data["train_name"], data["arrival_time"], data["reach_time"], data["journey_time"],
                        [(e[0], e[1]) for e in data["classes"]])

            info.append(req_info)

        # s_info = pickle.dump(info)

        msg = ''
        for row in info:
            # print(row)
            msg += row[0] + "\n" + ' ' * 15 + "Time: " + row[1] + " to " + row[2] + "(" + row[3] + ")"  + "\n" + ' ' * 15
            for c in row[4]:
                msg += str(c) + " "
            msg += "\n" + "\n" + ' ' * 15

        print(msg)

        return msg

    def train_schedule(self, train_no):
        url = "https://www.railyatri.in/time-table/" + str(train_no)

        table = []
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')

        schedules = soup.find_all('tbody')
        for schedule in schedules:
            row = []
            for e in schedule.find_all('td'):
                row.append(e.text.strip())
            table.append(row)

        msg = ""
        for r in table:
            # print(r)
            # msg += "{:>25} {:>10} {:>9} {:>7}".format(r[0], r[1], r[2], r[3]) + "\n" + ' '*15
            msg += str(r) + "\n" + ' '*15

        print(msg)
        return msg

    def pnr_status(self, pnr_no):
        url = "https://www.railyatri.in/pnr-status/" + str(pnr_no)
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html5lib')

            pnr_info = {}
            pnr_result = soup.find('div', class_="pnr-search-result-title").find('div', class_='row')
            for div in pnr_result:
                l = []
                for p in div:
                    if isinstance(p, bs4.element.Tag):
                        l.append(p.text.strip())
                if len(l) == 2:
                    pnr_info[l[0]] = l[1]

            train_route = soup.find('div', class_="train-route").find_all('div', class_="col-xs-4")
            for div in train_route:
                l = []
                for p in div:
                    if isinstance(p, bs4.element.Tag):
                        l.append(p.text.strip())

                if len(l) == 3:
                    pnr_info[l[0]] = l[1], l[2]

            boarding_details = soup.find('div', class_="boarding-detls").find_all('div', class_='col-xs-4')
            for div in boarding_details:
                l = []
                for p in div:
                    if isinstance(p, bs4.element.Tag):
                        l.append(p.text.strip())
                if len(l) == 2:
                    pnr_info[l[0]] = l[1]


            m = ''.join(e for e in str(pnr_info) if e != '{' or e != '}').split(',')
            print(m)
            msg = ''
            for el in m:
                msg += el + '\n' + ' '*15

            print(msg)
            print(pnr_info)
            return msg

        except:
            print("f")
            return "wrong pnr number"


if __name__ == '__main__':
    # fr = input("enter from station:")
    # to = input("enter to station:")
    # d = input("enter date (DD-MM-YYYY) :")
    # Railway().train_between_station(fr, to, d)
    fr = input("tno: ")
    Railway().train_schedule(fr)
