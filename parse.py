#!/usr/bin/env python3

import json
import os
import re

DATA_PATH = 'data'
WRITE_BACK_FILE = False

REQUIRED_KEYS = [
    'type',
    'authors',
    'title',
    'year',
    'venue',
]

SORTED_KEYS = [
    'type',
    'authors',
    'title',
    'venue',
    'year',

    'publisher',
    'address',
    'keywords',
    'pages',
    'month',
    'volume',
    'chapter',
    'editor',
    'organization',
    'note',
    'series',
    'number',
    'doi',
    'edition',

    'links',

    'abstract',
]

# In Python3, dicts remember the order that keys were inserted (and will iterate in that order).
# The json library will use that ordering when outputting.
# So, we will iterate through the keys in our order and put them into a new dict in the correct order.
def sortKeys(data):
    newData = {}

    keys = sorted(list(data.keys()), key = lambda key: SORTED_KEYS.index(key))
    for key in keys:
        newData[key] = data[key]

    return newData

def titlecase(title):
    lowercase = ['a', 'an', 'and', 'at', 'between', 'but', 'by', 'for', 'in', 'the', 'to', 'of', 'on', 'or', 'with']
    fixes = {
        'Psl': 'PSL',
        'Mltrain': 'MLtrain',
        'Max Sat': 'MAX SAT',
        'Map Inference': 'MAP Inference',
        'Large-Margin': 'Large-margin',
        'Mpe Inference': 'MPE Inference',
        'Voila:': 'VOILA:',
        ': a': ': A',
        ': the': ': The',
        'Mrfs': 'MRFs',
        'Standardgamble': 'StandardGamble',
        'Prl:': 'PRL:',
        'Relly:': 'RELLY:',
        'Hawkestopic:': 'HawkesTopic:',
        'Pxml:': 'PXML:',
        'Xml': 'XML',
        'Rna': 'RNA',
        'Spliceport - an': 'SplicePort - An',
        'Geoddupe:': 'GeoDDupe:',
        'La-Lda:': 'LA-LDA:',
        'C-Group:': 'C-GROUP:',
        'Hyper:': 'HyPER:',
        'in Collage': 'in COLLAGE',
        'Pac-Bayesian': 'PAC-Bayesian',
        'Pac-Bayes': 'PAC-Bayes',
        'Grdb:': 'GrDB:',
        'Taci:': 'TACI:',
        'Embers:': 'EMBERS:',
        'Mooc': 'MOOC',
        'Lda': 'LDA',
        'Sourceseer:': 'SourceSeer:',
        'Sourcesight:': 'SourceSight:',
        'Pagerank': 'PageRank',
        'Prdb:': 'PrDB:',
        'G-Pare:': 'G-PARE:',
        'Bowl:': 'BOWL:',
        'Homer:': 'HOMER:',
        'in Aa': 'in AA',
    }

    title = title.title()

    for word in lowercase:
        title = re.sub(r'\b%s\b' % (word), word, title, flags = re.IGNORECASE)

    title = title[0].upper() + title[1:]

    for (find, replace) in fixes.items():
        title = title.replace(find, replace)

    return title

def main():
    for dirent in sorted(os.listdir(DATA_PATH)):
        path = os.path.join(DATA_PATH, dirent)

        # TEST
        # print(path)

        with open(path, 'r') as file:
            data = sortKeys(json.load(file))

        for requiredKey in REQUIRED_KEYS:
            if (requiredKey not in data):
                raise ValueError("Could not find requried key (%s) in %s." % (requiredKey, path))

        firstAuthor = data['authors'][0]
        lastName = firstAuthor.split(' ')[-1]

        if (not dirent.startswith(lastName.lower())):
            # print("mv -i '%s' '%s'" % (path, re.sub(r'/\w+-', "/%s-" % (lastName.lower()), path)))
            raise ValueError("Filename should start with author last name (%s): [%s]." % (lastName.lower(), path))

        data['title'] = titlecase(data['title'])

        if (WRITE_BACK_FILE):
            with open(path, 'w') as file:
                json.dump(data, file, indent = 4)

if (__name__ == '__main__'):
    main()
