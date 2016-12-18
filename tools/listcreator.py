#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
from argparse import ArgumentParser

parser = ArgumentParser(description='Configure the SmartKey.')
parser.add_argument('--category', dest='category', action='store_true')
parser.add_argument('--emoji', dest='emoji', action='store_true')
args = parser.parse_args()

inList = sorted(json.load(sys.stdin).values(), key=lambda k: int(k['emoji_order']))

# for k in inList:
#     print(k['emoji_order'])
outList = []

for value in inList:
    if value['category'] != 'modifier':
        if args.emoji:
            keyCode = []
            for code in value['unicode'].split('-'):
                keyCode.append(int('0x{}'.format(code), base=16))
            # keyCode = '0x{}'.format(value['unicode'])
            print(type(keyCode))
            keywords = (value['name'] + ' ' + ' '.join(value['keywords']).strip()).strip()
            if 0x1f596 in keyCode:
                keywords += ' vulcan spock'
            elif 0x1f923 in keyCode:
                keywords += ' rofl'
            elif 0x2615 in keyCode:
                keywords += ' coffee'
            filename = './png/{}.png'.format(value['unicode'])
            category = value['category']
            outList.append([keyCode, keywords, filename, category])
        elif args.category:
            if not value['category'] in outList:
                outList.append(value['category'])

json.dump(outList, sys.stdout, indent=2)
