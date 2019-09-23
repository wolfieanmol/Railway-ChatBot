import math
import pickle
import nltk
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from nltk.stem.lancaster import LancasterStemmer
import socket_client

from entity import Entity
from railway import Railway


class Intent:
    def __init__(self):
        self.stemmer = LancasterStemmer()
        with open('intents_data.json', 'r') as json_data:
            self.intents = json.load(json_data)
            # print(self.intents)

    def create_vocab(self):
        intent_categories = []
        vocab = []
        documents = []
        for intent in self.intents['intents']:
            for query in intent['patterns']:
                query = ''.join(ch for ch in query if ch.isalnum() or ch.isspace())
                tokens = nltk.word_tokenize(query)
                vocab.extend(tokens)
                documents.append((tokens, intent['tag']))
            intent_categories.append(intent['tag'])

        vocab = [self.stemmer.stem(word.lower()) for word in vocab]
        vocab = sorted(list(set(vocab)))

        return vocab, documents, intent_categories

    def create_training_data(self):
        vocab, documents, intent_categories = self.create_vocab()
        training = []
        for doc in documents:
            x = []
            y = []
            for word in vocab:
                x.append(1) if word in [self.stemmer.stem(w.lower()) for w in doc[0]] else x.append(0)  # vocab 150
            # print(len(x))

            for catg in intent_categories:
                y.append(1) if catg == doc[1] else y.append(0)  # catg 8
            # print(y)

            training.append([x, y])

        training = np.array(training)
        np.random.shuffle(training)
        # print(training.shape)
        # print((list(training)))
        # print(training[0, :][1])
        return training


class IntentModel(nn.Module):
    def __init__(self, train_X, train_Y):
        super(IntentModel, self).__init__()

        # self.train_data = torch.tensor(train_data)
        # self.X = self.train_data[:, 0, :]
        # self.Y = self.train_data[:, 1, :]
        self.input_size = train_X[0].shape[1]
        self.hidden_size = 10
        self.output_size = train_Y[0].shape[1]

        self.lin1 = nn.Linear(self.input_size, self.hidden_size, bias=True)
        nn.init.xavier_uniform_(self.lin1.weight)
        self.lin2 = nn.Linear(self.hidden_size, self.hidden_size, bias=True)
        nn.init.xavier_uniform_(self.lin2.weight)
        self.lin3 = nn.Linear(self.hidden_size, self.output_size, bias=True)
        nn.init.xavier_uniform_(self.lin3.weight)

    def forward(self, X):
        x = self.lin1(X)
        x = F.relu(x)
        x = self.lin2(x)
        x = F.relu(x)
        x = self.lin3(x)

        return x


class TrainIntent:
    def minibatches(self, batch_size, train_data):
        m = []
        for i in range(0, train_data.shape[0], batch_size):
            m.append(train_data[i:batch_size + i, :])
        return m

    def train(self, n_epoch, batch_size, train_data):

        minibatches = self.minibatches(batch_size, train_data)
        # n_minibatches = math.ceil(train_data.shape[0] / batch_size)
        train_X = [np.array(list(t[:, 0])) for t in minibatches]
        train_Y = [np.array(list(t[:, 1])) for t in minibatches]

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = IntentModel(train_X, train_Y)
        # print(model)

        optimizer = torch.optim.Adam(model.parameters())
        loss_fn = nn.CrossEntropyLoss()

        model.to(device)
        model.train()

        for e in range(n_epoch):
            print("Epoch {} out of {}".format(e + 1, n_epoch))

            for x, y in zip(train_X, train_Y):
                optimizer.zero_grad()
                loss = 0
                # print(x.shape)
                x = torch.from_numpy(x).float().to(device)
                y = train_y = torch.from_numpy(y.nonzero()[1]).long().to(device)
                # Y = y.clone().detach()

                # print(x.type())
                # print(y.type())
                # print(Y)

                y_hat = model.forward(x)

                # print(y_hat.type())
                # print(y, Y.size(), "\n\n#######################################################")
                # print(y_hat, y_hat.size(), "\n\n#######################################################")

                loss = loss_fn(y_hat, y)
                loss.backward()
                optimizer.step()
                print("loss = {}".format(loss))

        torch.save(model.state_dict(), "intent.weights")
        pickle.dump({'train_x': train_X, 'train_y': train_Y},
                    open("training_data", "wb"))


# o = Intent().create_vocab()
# print(o[0], len(o[0]))
# print(o[1], len(o[1]))
# print(o[2], len(o[2]))

class InferIntent:
    def __init__(self):
        self.stemmer = LancasterStemmer()
        self.data = pickle.load(open("training_data", "rb"))

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = IntentModel(self.data["train_x"], self.data["train_y"])
        self.model.to(self.device)

        self.model.load_state_dict(torch.load("intent.weights"))

        self.model.eval()
        self.th = 0.3

    def clean_up_sentence(self, sentence):
        # tokenizing the pattern
        sentence_words = nltk.word_tokenize(sentence)
        # stemming each word
        sentence_words = [self.stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words

    # returning bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def bow(self, sentence, words, show_details=False):
        # tokenizing the pattern
        sentence_words = self.clean_up_sentence(sentence)
        # generating bag of words
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        b = np.array(bag).reshape(1, 148)
        # print(np.array(list(b)))
        return b

    def classify(self, sentence, vocab, intent_categories):
        # generate probabilities from the model
        x = torch.from_numpy(self.bow(sentence, vocab)).float().to(self.device)
        results = self.model.forward(x)
        # print(results)
        class_detected = results.argmax().tolist()
        return intent_categories[class_detected]

#
# if __name__ == '__main__':
#     with open("bot_login.txt", "r") as f:
#         d = f.read().split(",")
#         ip = d[0]
#         port = int(d[1])
#         username = d[2]
#     socket_client.connect(ip, 1234, username, show_error)
#
#     # TrainIntent().train(1000, 8, Intent().create_training_data())
#     vocab, documents, intent_categories = Intent().create_vocab()
#     # print(intent_categories)
#     i = InferIntent()
#
#     query = "i want to book a ticket to mumbai"
#     if isinstance(query, str):
#         intent = i.classify(query, vocab, intent_categories)
#         print(intent)
#
#         if intent == "train_reservation":
#             # print(1)
#             en = Entity()
#             slots = en.entity_recog(query)
#             print(slots)
#             while slots['to_city'] is None or slots['from_city'] is None or slots['date'] is None:
#                 # print(2)
#                 if slots['to_city'] is None:
#                     socket_client.send("Where do you want to travel to?")
#                     query = socket_client.start_listening(incoming_message, show_error)
#                     if isinstance(query, str):
#                         slots = en.get_to(query)
#                         print(slots)
#
#                 elif slots['from_city'] is None:
#                     socket_client.send("where will you be boarding the train?")
#                     query = socket_client.start_listening(incoming_message, show_error)
#                     if isinstance(query, str):
#                         slots = en.get_from(query)
#                         print(slots)
#
#                 elif slots['date'] is None and slots['month'] is None:
#                     socket_client.send("At what date to you want to travel?")
#                     query = socket_client.start_listening(incoming_message, show_error)
#                     if isinstance(query, str):
#                         slots = en.get_date(query)
#                         print(slots)
#             date = str(slots['date']) + '-' + str(slots['month']) + '-' + str(slots['year'])
#
#             Railway().train_between_station(slots['from_city'], slots['to_city'], date)
