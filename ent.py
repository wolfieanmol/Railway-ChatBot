#!/usr/bin/env python
# coding: utf8

# Training additional entity types using spaCy
from __future__ import unicode_literals, print_function
import pickle
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding


# New entity labels
# Specify the new entity labels which you want to add here
LABEL = ['to_city', 'from_city', 'DATE', 'class']

"""
geo = Geographical Entity
org = Organization
per = Person
gpe = Geopolitical Entity
tim = Time indicator
art = Artifact
eve = Event
nat = Natural Phenomenon
"""
# Loading training data
# with open ('Data/ner_corpus_260', 'rb') as fp:
TRAIN_DATA = [('I need a ticket to jaipur today', {'entities': [(19, 24, 'to_city')]}),
              ('Have to travel to jodhpur for 2 days', {'entities': [(18, 24, 'to_city')]}),
              ('show me trains for Chennai on 17th august.', {'entities': [(19, 25, 'to_city'), (30, 40, 'DATE')]}),
              ('Please book a journey to Haridwar for 3 people', {'entities': [(25, 32, 'to_city')]}),
              ('I need to travel to shimla', {'entities': [(20, 25, 'to_city')]}),
              ("I'm looking for a train from New Delhi to Ahmedabad on the 21th of this month.", {'entities': [(29, 37, 'from_city'), (42, 50, 'to_city'), (59, 76, 'DATE')]}),
              ('Hi book me a ticket for kolkata.', {'entities': [(24, 30, 'to_city')]}),
              ('me and my friends are going for a vacation to goa', {'entities': [(46, 48, 'to_city')]}),
              ("I need to go to hyderabad to attend my sister's wedding", {'entities': [(16, 24, 'to_city')]}),
              ('My dad needs to visit amritsar on 17 january', {'entities': [(22, 29, 'to_city'), (34, 43, 'DATE')]}),
              ("I need to travel to Mumbai in order to attend a meeting", {'entities': [(20, 25, 'to_city')]}),
              ('I need 3 3rd AC resevations on july 28 to Trivendram', {'entities': [(9, 14, 'class'), (31, 37, 'DATE'), (42, 51, 'to_city')]}),
              ('Have a meeting a day after tomorrow in pune', {'entities': [(17, 34, 'DATE'), (39, 42, 'to_city')]}),
              ('I need to get to Guwhati.', {'entities': [(17, 23, 'to_city')]}),
              ('Going to mumbai', {'entities': [(9, 14, 'to_city')]}),
              ('shifting from delhi to manali via train', {'entities': [(14, 18, 'from_city'), (23, 28, 'to_city')]}),
              ('send me to delhi', {'entities': [(11, 15, 'to_city')]}),
              ('I have to book a ticket from jabalpur to gandhinagar for me and my friend on 27 aug in a 3 ac coach', {'entities': [(29, 36, 'from_city'), (41, 51, 'to_city'), (77, 82, 'DATE'), (89, 92, 'class')]}),
              ("For my sister's wedding I need to go to chandigarh from ajmer on 3rd of next month", {'entities': [(40, 49, 'to_city'), (56, 60, 'from_city'), (65, 81, 'DATE')]}),
              ("What is the ticket fare to mumbai from Ahembadabad for sleeper class?", {'entities': [(27, 32, 'to_city'), (39, 49, 'from_city'), (55, 67, 'class')]})]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))

def main(model=None, new_model_name='new_model', output_dir=None, n_iter=10):
    """Setting up the pipeline and entity recognizer, and training the new entity."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spacy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe('ner')

    for i in LABEL:
        ner.add_label(i)   # Add new entity labels to entity recognizer

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.entity.create_optimizer()

    # Get names of other pipes to disable them during training to train only NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=1024)
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.0,
                           losses=losses)
            print('Losses', losses)
            print(itn)

    # Test the trained model
    test_text = 'book me a train from chennai to goa tomorrow'
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # Save model
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # Test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    plac.call(main)