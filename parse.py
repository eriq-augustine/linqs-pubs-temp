#!/usr/bin/env python3

import json
import os
import re

DATA_PATH = 'data'
WRITE_BACK_FILE = False

ALLOWED_TYPES = {'article', 'book', 'conference', 'inbook', 'phdthesis', 'techreport', 'tutorial', 'unpublished'}

REQUIRED_KEYS = [
    'type',
    'authors',
    'title',
    'year',
    'venue',
]

SKIP_KEYS = [
    'month',
    'series',
]

# Keys (outside of REQUIRED_KEYS) that are required for specific types.
TYPE_FIELDS = {
    'article': {'number', 'pages', 'volume'},
    'book': {'edition', 'publisher'},
    'conference': set(),
    'inbook': {'edition', 'editor', 'pages', 'publisher'},
    'phdthesis': set(),
    'techreport': set(),
    'tutorial': set(),
    'unpublished': set(),
}

SORTED_KEYS = [
    # Core.
    'type',
    'title',
    'authors',
    'venue',
    'year',

    # Type-dependent.
    'pages',
    'volume',
    'number',
    'edition',
    'editor',
    'publisher',

    # Extra.
    'chapter',
    'address',
    'organization',
    'doi',
    'note',

    # Variable size.
    'keywords',
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
        if (key in SKIP_KEYS):
            continue

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

def validateEntry(filename, data):
    for requiredKey in REQUIRED_KEYS:
        if (requiredKey not in data):
            raise ValueError("Could not find requried key (%s) in %s." % (requiredKey, filename))

    if (data['type'] not in ALLOWED_TYPES):
        raise ValueError("Unknown type (%s) in %s." % (data['type'], filename))

    firstAuthor = data['authors'][0]
    lastName = firstAuthor.split(' ')[-1]
    filenameLastName = re.sub(r'\*$', '', lastName.lower())

    if (not filename.startswith(filenameLastName)):
        raise ValueError("Filename (%s) should start with author last name (%s)." % (filename, filenameLastName))

    if (not re.search(r'%s([a-z]?)\.json$' % (data['year'][-2:]), filename)):
        raise ValueError("Filename (%s) should end with the correct year: %s (%s)." % (filename, data['year'], data['year'][-2:]))

    for requiredKey in TYPE_FIELDS[data['type']]:
        if (requiredKey not in data):
            raise ValueError("File (%s) of type (%s) does not contain the required field: '%s'." % (filename, data['type'], requiredKey))

def main():
    for dirent in sorted(os.listdir(DATA_PATH)):
        path = os.path.join(DATA_PATH, dirent)

        with open(path, 'r') as file:
            data = sortKeys(json.load(file))

        validateEntry(dirent, data)

        data['title'] = titlecase(data['title'])

        if (WRITE_BACK_FILE):
            with open(path, 'w') as file:
                json.dump(data, file, indent = 4)
                file.write("\n")

if (__name__ == '__main__'):
    main()
