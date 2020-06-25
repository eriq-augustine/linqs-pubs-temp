#!/usr/bin/env python3

import json
import os

DATA_PATH = 'data'

def main():
    for dirent in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, dirent)

        # TEST
        print(path)

        with open(path, 'r') as file:
            data = json.load(file)

        # TEST
        # print(path)
        # print(data)
        # break

if (__name__ == '__main__'):
    main()
