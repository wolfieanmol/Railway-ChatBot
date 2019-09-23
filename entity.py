import json
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

nlp = en_core_web_sm.load()
from pprint import pprint
import pickle


class Entity:
    def __init__(self):

        with open("stations.json") as f:
            self.stations = json.load(f)

        with open("cities", "rb") as f:
            self.cities = pickle.load(f)

        self.date_parse = {
            'legal_dates': [str(i).zfill(1) for i in range(1, 10)] + [str(i).zfill(2) for i in range(1, 32)],
            'legal_years': list(range(2019, 2025)),
            'legal_days': ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "mon", "tue",
                           "tues",
                           "wed", "wed", "thurs", "thu", "fri", "sat", "sun"],

            'legal_months':
                {
                    '01': ["1", "01", "january", "jan"],
                    '02': ["2", "02", "february", "feb"],
                    '03': ["3", "03", "march", "mar"],
                    '04': ["4", "04", "april", "apr"],
                    '05': ["5", "05", "may", "june"],
                    '06': ["6", "06", "jun", "july"],
                    '07': ["7", "07", "jul"],
                    '08': ["8", "08", "august", "aug"],
                    '09': ["9", "09", "september", "sep"],
                    '10': ["10", "october", "oct"],
                    '11': ["11", "november", "nov"],
                    '12': ["12", "december", "dec"],
                },
            'legal_det': ["today", "tomorrow", "the next day", "next day", "yesterday", "previous day",
                          "the previous day",
                          "next week", "next month"]
        }

        self.slots = {
            'to_city': None,
            'from_city': None,
            'date': None,
            'month': None,
            'year': 2019
        }

    def entity_recog(self, query):
        # self.slots = {
        #     'to_city': None,
        #     'from_city': None,
        #     'date': None,
        #     'month': None,
        #     'year': 2019
        # }

        # query = "I'm going on a vacation with my friends for jaipur from ajmer on september 27"
        s = query.lower().split()
        to_ = ['in', 'to', 'for', 'visit']
        from_ = ['from']
        for i in range(len(s)):
            for city in self.cities:
                if s[i] == city.lower() and s[i - 1] in from_:
                    self.slots['from_city'] = city.lower()
                elif s[i] == city.lower() and s[i - 1] in to_:
                    self.slots['to_city'] = city.lower()

        self.get_date(query)

        return self.slots

    def get_date(self, query):
        doc = nlp(query)
        ent = [(X.text, X.label_) for X in doc.ents]
        # print(ent)
        for e in ent:
            if e[1] == "DATE":
                date = e[0].split()
                for d in date:
                    if d in self.date_parse['legal_dates']:
                        # print(d)
                        self.slots['date'] = d

                    else:
                        for key in self.date_parse['legal_months'].keys():
                            # print(key)
                            if d in self.date_parse['legal_months'][key]:
                                # print(key)
                                self.slots['month'] = key

                # print(self.slots)

                date = str(self.slots['date']) + '-' + str(self.slots['month']) + '-' + str(self.slots['year'])
                # print(date)
        print("@@@@", self.slots)
        return self.slots

    def get_from(self, query):
        s = query.lower().split()
        to_ = ['in', 'to', 'for', 'visit']
        for i in range(len(s)):
            for city in self.cities:
                if s[i] == city.lower():
                    self.slots['from_city'] = city.lower()
                elif s[i] == city.lower() and s[i - 1] in to_:
                    self.slots['to_city'] = city.lower()

        return self.slots

    def get_to(self, query):
        s = query.lower().split()
        to_ = ['in', 'to', 'for', 'visit']
        from_ = ['from']
        for i in range(len(s)):
            for city in self.cities:
                if s[i] == city.lower() and s[i - 1] in from_:
                    self.slots['from_city'] = city.lower()
                elif s[i] == city.lower():
                    self.slots['to_city'] = city.lower()

        return self.slots
