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

def main():
    for dirent in sorted(os.listdir(DATA_PATH)):
        path = os.path.join(DATA_PATH, dirent)

        # TEST
        # print(path)

        with open(path, 'r') as file:
            data = json.load(file)

        for requiredKey in REQUIRED_KEYS:
            if (requiredKey not in data):
                raise ValueError("Could not find requried key (%s) in %s." % (requiredKey, path))

        firstAuthor = data['authors'][0]
        lastName = firstAuthor.split(' ')[-1]

        if (not dirent.startswith(lastName.lower())):
            # print("mv -i '%s' '%s'" % (path, re.sub(r'/\w+-', "/%s-" % (lastName.lower()), path)))
            raise ValueError("Filename should start with author last name (%s): [%s]." % (lastName.lower(), path))

if (__name__ == '__main__'):
    main()
