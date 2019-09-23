import socket_client
from entity import Entity
from intent import InferIntent, Intent
from railway import Railway
from selenium import webdriver
import numpy.random as random


class Inference:
    def __init__(self):
        self.count = 0
        socket_client.connect("127.0.0.1", 1234, "RailBot", self.show_error)

        self.vocab, self.documents, self.intent_categories = Intent().create_vocab()

        self.i = InferIntent()
        self.en = Entity()

        self.slots = {}
        self.pnr = None
        self.date = None
        self.intent = None

        self.query = socket_client.start_listening(self.incoming_message, self.show_error)
        self.message = ''
        # self.choose_train = False

    def detect_intent(self):
        self.slots = {
            'to_city': None,
            'from_city': None,
            'date': None,
            'month': None,
            'year': 2019
        }
        intent = self.i.classify(self.message, self.vocab, self.intent_categories)
        self.intent = intent
        print(intent)

        if intent == "train_reservation":
            self.get_entities()

        elif intent == "greeting":
            responses = ["hey, I'm RailBot", "Hi there", "hey"]
            socket_client.send(random.choice(responses))
            self.message = ''
            self.count = 0

        elif intent == "goodbye":
            responses = ['See you later, thanks for visiting', 'Have a nice day', 'Bye! Come back again soon.']
            socket_client.send(random.choice(responses))
            self.message = ''
            self.count = 0

        elif intent == "pnr_status":
            self.get_pnr()
            self.message = ''

        elif intent == "thanks":
            responses = ['Happy to help!', 'Any time!', 'My pleasure']
            socket_client.send(random.choice(responses))
            self.message = ''
            self.count = 0

        elif intent == "train_schedule":
            if self.message != '':
                print("######")
                l = self.message.split(' ')
                print(l)
                x = None
                for e in l:
                    try:
                        int(e)
                        x = int(e)
                        print(x)
                    except:
                        pass
                if x:
                    pnr = Railway().train_schedule(x)
                    socket_client.send(pnr)
                    self.count = 0
                else:
                    socket_client.send("wrong train number")
                    self.count = 0
        else:
            self.count = 0

    def get_pnr(self):
        if self.pnr:
            if len(self.pnr) == 10:
                pnr = Railway().pnr_status(self.pnr)
                socket_client.send(pnr)
                self.count = 0
            else:
                socket_client.send("wrong pnr number")
                self.count = 0

        else:
            responses = ['What is your pnr number?', 'Can You tell me what your PNR number is?',
                         'Ok, sure tell me your pnr number', 'please tell me your pnr number']
            socket_client.send(random.choice(responses))
            self.message = ''
            self.get_pnr_from_user()

    def get_pnr_from_user(self):
        # self.message = ''

        if self.message != '':
            print("######")
            l = self.message.split(' ')
            print(l)
            x = None
            for e in l:
                try:
                    int(e)
                    x = int(e)
                    print(x)
                except:
                    pass
            if x:
                pnr = Railway().pnr_status(x)
                socket_client.send(pnr)
                self.count = 0
            else:
                socket_client.send("wrong pnr number")
                self.count = 0

    def get_entities(self):
        self.slots = self.en.entity_recog(self.message)
        self.message = ''
        # self.next_action()

        if self.slots['to_city'] is None:
            socket_client.send("Where do you want to travel to?")

        elif self.slots['from_city'] is None:
            socket_client.send("Where will you be boarding the train from?")

        elif self.slots['date'] is None or self.slots['month'] is None:
            socket_client.send("At what date to you want to travel?")

    def get_to_city(self):

        if self.message != '':
            self.slots = self.en.get_to(self.message)
            print(self.slots)
            self.message = ''
            # self.next_action()
            if self.slots['to_city'] is None:
                socket_client.send("Where do you want to travel to?")

            elif self.slots['from_city'] is None:
                socket_client.send("Where will you be boarding the train from?")

            elif self.slots['date'] is None or self.slots['month'] is None:
                socket_client.send("At what date to you want to travel?")

            else:
                train_info = Railway().train_between_station(self.slots['from_city'], self.slots['to_city'],
                                                             str(self.slots['date']) + '-' + str(
                                                                 self.slots['month']) + '-' + str(
                                                                 self.slots['year']))
                self.slots['to_city'] = None
                self.slots['from_city'] = None
                self.slots['date'] = None
                self.slots['month'] = None
                self.slots['year'] = None
                self.slots = {}
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", self.slots)
                socket_client.send(train_info)
                # socket_client.send("Which train do you want to choose?")
                # self.choose_train = True
                self.message = ''
                self.count = 0

    def get_from_city(self):

        if self.message != '':
            print("whoh")
            print(self.message)
            print('111')
            self.slots = self.en.get_from(self.message)
            print(self.slots)
            self.message = ''
            # self.next_action()
            if self.slots['to_city'] is None:
                socket_client.send("Where do you want to travel to?")

            elif self.slots['from_city'] is None:
                socket_client.send("Where will you be boarding the train from?")

            elif self.slots['date'] is None or self.slots['month'] is None:
                socket_client.send("At what date to you want to travel?")

            else:
                train_info = Railway().train_between_station(self.slots['from_city'], self.slots['to_city'],
                                                             str(self.slots['date']) + '-' + str(
                                                                 self.slots['month']) + '-' + str(
                                                                 self.slots['year']))
                self.slots['to_city'] = None
                self.slots['from_city'] = None
                self.slots['date'] = None
                self.slots['month'] = None
                self.slots['year'] = None
                self.slots = {}
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", self.slots)
                socket_client.send(train_info)
                self.message = ''
                self.count = 0
                # socket_client.send("Which train do you want to choose?")
                # self.choose_train = True

    def get_date(self):

        if self.message != '':
            self.slots = self.en.get_date(self.message)
            print(self.slots)
            self.date = str(self.slots['date']) + '-' + str(self.slots['month']) + '-' + str(self.slots['year'])
            self.message = ''
            self.next_action()
            if self.slots['to_city'] is None:
                socket_client.send("Where do you want to travel to?")

            elif self.slots['from_city'] is None:
                socket_client.send("Where will you be boarding the train from?")

            elif self.slots['date'] is None or self.slots['month'] is None:
                socket_client.send("At what date to you want to travel?")

            else:
                train_info = Railway().train_between_station(self.slots['from_city'], self.slots['to_city'],
                                                             str(self.slots['date']) + '-' + str(
                                                                 self.slots['month']) + '-' + str(
                                                                 self.slots['year']))
                self.slots['to_city'] = None
                self.slots['from_city'] = None
                self.slots['date'] = None
                self.slots['month'] = None
                self.slots['year'] = None
                self.slots = {}
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", self.slots)
                socket_client.send(train_info)
                self.message = ''
                self.count = 0
                # socket_client.send("Which train do you want to choose?")
                # self.choose_train = True
                print(self.count)

    def next_action(self):
        if self.slots['to_city'] is None:
            print(1)
            self.get_to_city()
        elif self.slots['from_city'] is None:
            self.get_from_city()
        elif self.slots['date'] is None or self.slots['month'] is None:
            self.get_date()
        else:
            train_info = Railway().train_between_station(self.slots['from_city'], self.slots['to_city'],
                                                         str(self.slots['date']) + '-' + str(
                                                             self.slots['month']) + '-' + str(
                                                             self.slots['year']))
            self.slots['to_city'] = None
            self.slots['from_city'] = None
            self.slots['date'] = None
            self.slots['month'] = None
            self.slots['year'] = None
            self.slots = {}
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", self.slots)
            socket_client.send(train_info)
            self.message = ''
            # socket_client.send("Which train do you want to choose?")
            # self.choose_train = True
            self.count = 0

    # def choose(self):
    #     browser = webdriver.Chrome("/home/wolfie/PycharmProject/railway-chatbot/chromedriver")
    #     url = "https://www.railyatri.in/train-ticket/passengers-detail?action=get_token&boarding_date=29-9-2019&class=SL&controller=train_ticket%2Fbookings&doj=29-9-2019&from=AII&is_cached=true&probability=High&quota=GN&src=seat_availability&status=GNWL83%2FWL31.&to=BVI&train_name=AJMER+-+DADAR+SF+Express&train_no=12990&user_id=-1569069763&user_token=370262"
    #     browser.get(url)
    #     self.count = 0

    def show_error(self, message):
        print("!!!", message)

    def incoming_message(self, username, message):
        print(f'{username}>{message}')
        if isinstance(message, str):
            self.message = message
            if self.count == 0:
                inference.detect_intent()
                self.count += 1

            elif self.intent == "pnr_status":
                self.get_pnr_from_user()

            # elif self.choose_train:
            #     self.choose()
            else:
                self.next_action()


if __name__ == '__main__':
    inference = Inference()
