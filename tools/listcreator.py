#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os.path
from html.parser import HTMLParser
from argparse import ArgumentParser

class EmojiParser(HTMLParser):
    def __init__(self, imgPath):
        HTMLParser.__init__(self)
        self.imgpath = imgPath
        self.nextData = None
        self.Categories = []
        self.Emojis = []
        self.nextChar = []
        self.nextFilename = None
        return

    def handle_starttag (self, tag, attrs):
        if tag == 'th' and ('class', 'bighead') in attrs:
            print('Found Category...')
            self.nextData = 'category'
        elif tag == 'td' and ('class', 'code') in attrs:
            self.nextData = 'code'
        elif tag == 'td' and ('class', 'name') in attrs:
            self.nextData = 'name'
        return

    def handle_data(self, data):
        if self.nextData == 'category':
            print('Enter Category: {}'.format(data))
            self.Categories.append([data, [data.split()[0].lower()]])
            self.nextData = None
        elif self.nextData == 'code':
            codes = []
            fileBase = []
            for code in data.split():
                splt = code.split('+')[-1]
                codes.append(int(splt, 16))
                if splt != '200D' and splt != 'FE0F':
                    fileBase.append(splt)
            filename = '-'.join(fileBase).lower() + '.png'
            if os.path.exists(os.path.join(self.imgpath, filename)):
                self.nextFilename = os.path.join('.', 'png', filename)
            self.nextChar.append(codes)
            self.nextData = None
        elif self.nextData == 'name':
            if self.nextFilename != None:
                self.nextChar.append(data)
                self.nextChar.append(self.nextFilename)
                self.nextChar.append(self.Categories[-1][-1][0])
                self.Emojis.append(self.nextChar)
                # print(self.nextChar)
            self.nextChar = []
            self.nextFilename = None
            self.nextData = None
        return

parser = ArgumentParser(description='Configure the SmartKey.')
parser.add_argument('--img-path', dest='imgPath', required=True)
parser.add_argument('--html-file', dest='htmlFile', required=True)
# parser.add_argument('--category', dest='category', action='store_true')
# parser.add_argument('--emoji', dest='emoji', action='store_true')
args = parser.parse_args()

htmlData = open(args.htmlFile, 'r').read()
# print(htmlData)
emojiParser = EmojiParser(args.imgPath)
emojiParser.feed(htmlData)

allCat = []
for cat in emojiParser.Categories:
    allCat.append(cat[-1][0])
emojiParser.Categories.insert(0, ['All', allCat])
json.dump(emojiParser.Categories, open('category.json', 'w'), indent=2)
json.dump(emojiParser.Emojis, open('emoji.json', 'w'), indent=2)

# inList = sorted(json.load(sys.stdin).values(), key=lambda k: int(k['emoji_order']))
#
# # for k in inList:
# #     print(k['emoji_order'])
# outList = []
#
# for value in inList:
#     if value['category'] != 'modifier':
#         if args.emoji:
#             keyCode = []
#             for code in value['unicode'].split('-'):
#                 keyCode.append(int('0x{}'.format(code), base=16))
#             # keyCode = '0x{}'.format(value['unicode'])
#             print(type(keyCode))
#             keywords = (value['name'] + ' ' + ' '.join(value['keywords']).strip()).strip()
#             if 0x1f596 in keyCode:
#                 keywords += ' vulcan spock'
#             elif 0x1f923 in keyCode:
#                 keywords += ' rofl'
#             elif 0x2615 in keyCode:
#                 keywords += ' coffee'
#             filename = './png/{}.png'.format(value['unicode'])
#             category = value['category']
#             outList.append([keyCode, keywords, filename, category])
#         elif args.category:
#             if not value['category'] in outList:
#                 outList.append(value['category'])
#
# json.dump(outList, sys.stdout, indent=2)
