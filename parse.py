#!/usr/bin/env python3

import json
import os
import re

DATA_PATH = 'data'
MANUAL_PATH = 'manual.tsv'
VENUES_PATH = 'venues.json'

WRITE_BACK_FILE = False

ALLOWED_TYPES = {'article', 'book', 'conference', 'inbook', 'phdthesis', 'techreport', 'tutorial', 'unpublished'}

REQUIRED_KEYS = [
    'type',
    'authors',
    'title',
    'year',
    'venue',
    'publisher',
]

SKIP_KEYS = [
    'month',
    'series',
]

# Keys (outside of REQUIRED_KEYS) that are required for specific types.
TYPE_FIELDS = {
    'article': {'number', 'pages', 'volume'},
    'book': {'edition'},
    'conference': {'address'},
    'inbook': {'edition', 'editor', 'pages'},
    'phdthesis': {'address'},
    'techreport': set(),
    'tutorial': {'address'},
    'unpublished': set(),
}

SORTED_KEYS = [
    # Core.
    'type',
    'title',
    'authors',
    'venue',
    'year',
    'publisher',

    # Type-dependent.
    'pages',
    'volume',
    'number',
    'edition',
    'editor',
    'address',

    # Extra.
    'chapter',
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
        'Srl': 'SRL',
        'Mltrain': 'MLtrain',
        'Max Sat': 'MAX SAT',
        'Map Inference': 'MAP Inference',
        'Large-Margin': 'Large-margin',
        'Mpe Inference': 'MPE Inference',
        'Voila:': 'VOILA:',
        ': a': ': A',
        ': the': ': The',
        'Mrfs': 'MRFs',
        'Hl-MRFs': 'HL-MRFs',
        'Standardgamble': 'StandardGamble',
        'Prl:': 'PRL:',
        'Relly:': 'RELLY:',
        'Hawkestopic:': 'HawkesTopic:',
        'Pxml:': 'PXML:',
        'Xml': 'XML',
        'Rna': 'RNA',
        'Vs.': 'vs.',
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

def loadManualFile():
    manualData = {}

    with open(MANUAL_PATH, 'r') as file:
        first = True
        for line in file:
            if (first):
                first = False
                continue

            line = line.strip()
            if (line == ''):
                continue

            parts = line.split("\t")
            if (len(parts) == 7):
                parts.append('')

            manualData[parts[0]] = {
                'type': parts[1],
                'venueID': parts[2],
                'venueShortname': parts[3],
                'venue': parts[4],
                'year': parts[5],
                'publisher': parts[6],
                'address': parts[7],
            }

    # Collect venue information.
    venues = {}
    for data in manualData.values():
        if (data['type'] in {'book', 'phdthesis', 'techreport'}):
            continue

        venue = data['venue']
        id = data['venueID']
        shortname = data['venueShortname']

        if (venue not in venues):
            venues[venue] = {
                'id': id,
            }

            if (shortname != ''):
                venues[venue]['shortname'] = shortname
        else:
            if (venues[venue]['id'] != id):
                raise ValueError("Inconsistent venue ids. Venue: '%s', ids: ('%s', '%s')." % (venue, venues[venue]['id'], id))

            if (shortname != '' and venues[venue]['shortname'] != shortname):
                raise ValueError("Inconsistent venue shortnames. Venue: '%s', shortnames: ('%s', '%s')." % (venue, venues[venue]['shortname'], shortname))

    if (WRITE_BACK_FILE):
        with open(VENUES_PATH, 'w') as file:
            json.dump(venues, file, indent = 4, sort_keys = True)
            file.write("\n")

    return manualData

# Validate against a manually curated file.
def validateManualFile(manualDataFull, filename, data):
    if (filename not in manualDataFull):
        raise ValueError("Could not locate manual information for %s." % (filename))
    manualData = manualDataFull[filename]

    lastName = data['authors'][0].split(' ')[-1]
    filenameLastName = re.sub(r'\*$', '', lastName.lower())

    filenameRegex = r'^%s-%s%s[abc]?\.json$' % (filenameLastName, manualData['venueID'], data['year'][-2:])
    if (not re.match(filenameRegex, filename)):
        raise ValueError("Entry named incorrectly. Is: '%s', should be: '%s'." % (filename, filenameRegex))

    data['venue'] = manualData['venue']
    data['publisher'] = manualData['publisher']

    if (manualData['address'] != ''):
        data['address'] = manualData['address']

def fixKeywords(data):
    if ('keywords' not in data):
        return

    if (isinstance(data['keywords'], str)):
        text = titlecase(data['keywords'])
        keywords = [keyword.strip() for keyword in text.split(',')]
        data['keywords'] = keywords

def main():
    manualData = loadManualFile()

    for dirent in sorted(os.listdir(DATA_PATH)):
        path = os.path.join(DATA_PATH, dirent)

        with open(path, 'r') as file:
            data = sortKeys(json.load(file))

        validateEntry(dirent, data)
        validateManualFile(manualData, dirent, data)

        fixKeywords(data)

        data['title'] = titlecase(data['title'])

        if (WRITE_BACK_FILE):
            with open(path, 'w') as file:
                json.dump(data, file, indent = 4)
                file.write("\n")

if (__name__ == '__main__'):
    main()
