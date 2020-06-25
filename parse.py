#!/usr/bin/env python3

import json
import os
import re

DATA_PATH = 'data'

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

        # TEST
        with open(path, 'w') as file:
            json.dump(data, file, indent = 4)

if (__name__ == '__main__'):
    main()
