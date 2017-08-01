#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os.path
import requests
from html.parser import HTMLParser
from argparse import ArgumentParser


emojiListURL =  'http://unicode.org/emoji/charts/full-emoji-list.html'


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
            self.nextData = 'category'
        elif tag == 'td' and ('class', 'code') in attrs:
            self.nextData = 'code'
        elif tag == 'td' and ('class', 'name') in attrs:
            self.nextData = 'name'
        return

    def handle_data(self, data):
        if self.nextData == 'category':
            print('Reading Category: {}'.format(data))
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
parser.add_argument('--emojione-path', dest='imgPath', required=True)
parser.add_argument('--full-emoji-list', dest='emojiList')
args = parser.parse_args()

htmlData = None

if args.emojiList:
    print('Loading Emoji List from \'{}\''.format(args.htmlFile))
    htmlData = open(args.htmlFile, 'r').read()
else:
    print('Loading Emoji List from \'{}\''.format(emojiListURL))
    htmlData = requests.get(emojiListURL, timeout=30).content.decode('utf-8')

emojiParser = EmojiParser(args.imgPath)
emojiParser.feed(htmlData)

print('Found {} Emojis in {} Categories.'.format(len(emojiParser.Emojis), len(emojiParser.Categories)))

allCat = []
for cat in emojiParser.Categories:
    allCat.append(cat[-1][0])
emojiParser.Categories.insert(0, ['All', allCat])
json.dump(emojiParser.Categories, open('category.json', 'w'), indent=2)
json.dump(emojiParser.Emojis, open('emoji.json', 'w'), indent=2)
