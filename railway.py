import requests
from bs4 import BeautifulSoup
import json
import os
import time
from fuzzywuzzy import process


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

        param = {"from_code": from_station,
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

            data = {"train_number": train.attrs["data-number"],
                    "train_name": train.attrs["data-name"],
                    "runday": train.attrs["data-runday"],
                    "from_station": train.attrs["data-from"],
                    "to_station": train.attrs["data-to"],
                    "arrival_time": schedule[1].text,
                    "reach_time": schedule[4].text,
                    "journey_time": schedule[5].text,
                    "ontime": schedule[6].text,
                    "classes": [(e["data-coach"], e.div.find_all('p')[1].text, e["data-redirect_url"]) for e in fares]}

            info.append(data)

        for row in info:
            print(row)


if __name__ == '__main__':
    fr = input("enter from station:")
    to = input("enter to station:")
    d = input("enter date (DD-MM-YYYY) :")
    Railway().train_between_station(fr, to, d)
