#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
import json
import re
import os.path
from subprocess import check_output, run
from time import sleep

emojiStore = Gtk.ListStore(object, str, GdkPixbuf.Pixbuf, str)
modulePath = os.path.dirname(os.path.abspath(__file__))
for element in json.load(open(os.path.join(modulePath, './emoji.json'), 'r')):
    emojiStore.append([element[0], element[1], GdkPixbuf.Pixbuf.new_from_file(os.path.join(modulePath, element[2])), element[3]])
emojiCategorys = json.load(open(os.path.join(modulePath, './category.json')))
emptyPic = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes([0] * (64*64*4)), 0, True, 8, 64, 64, 64*4)

def get_pixbuf_from_unicode(keycode):
    for elem in emojiStore:
        if elem[0] == keycode:
            return elem[2]
    return emptyPic

class EmojiSelectorBox(Gtk.Box):
    def __init__(self, preselect=None):
        super(Gtk.Box, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        self.lockToggle = False
        self.selectedEmoji = preselect
        self.selectedCategorys = []

        self.categoryBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        for catKey, catVal in emojiCategorys:
            btn = Gtk.ToggleButton(catKey)
            btn.connect('clicked', self.on_category_button_clicked, catVal)
            self.categoryBox.pack_start(btn, True, True, 0)

        self.pack_start(self.categoryBox, False, True, 0)

        self.filterEntry = Gtk.Entry()
        self.filterEntry.connect('changed', self.on_filter_entry_changed)

        self.pack_start(self.filterEntry, False, True, 0)

        self.emojiFilter = emojiStore.filter_new()
        self.emojiFilter.set_visible_func(self.emoji_filter_func)

        self.emojiSorter = Gtk.TreeModelSort(model=self.emojiFilter)
        # self.emojiSorter.set_default_sort_func(self.emoji_sort_func, None)
        self.emojiSorter.set_sort_func(1, self.emoji_sort_func, None)

        emojiListView = Gtk.IconView.new_with_model(self.emojiSorter)
        emojiListView.set_pixbuf_column(2)
        emojiListView.set_selection_mode(Gtk.SelectionMode.BROWSE)
        for i, value in enumerate(self.emojiFilter):
            if value[0] == preselect:
                emojiListView.select_path(Gtk.TreePath.new_from_indices([i]))
                emojiListView.scroll_to_path(Gtk.TreePath.new_from_indices([i]), True, 0.5, 0.5)
        emojiListView.connect('selection-changed', self.on_emoji_icon_selected)

        for btn in self.categoryBox:
            if btn.get_label() == 'All':
                btn.set_active(True)

        scroll = Gtk.ScrolledWindow()
        scroll.add(emojiListView)

        self.pack_start(scroll, True, True, 0)

    def on_category_button_clicked(self, widget, category):
        if not self.lockToggle:
            if not widget.get_active():
                widget.set_active(True)
            else:
                self.lockToggle = True
                for btn in self.categoryBox:
                    if btn != widget:
                        btn.set_active(False)
                self.selectedCategorys = category
                self.emojiFilter.refilter()
                self.emojiSorter.set_sort_column_id(-1, 0)
                self.emojiSorter.set_sort_column_id(1, 0)
                self.lockToggle = False

    def on_filter_entry_changed(self, widget):
        print(self.filterEntry.get_text().split(' '))
        self.emojiFilter.refilter()
        self.emojiSorter.set_sort_column_id(-1, 0)
        self.emojiSorter.set_sort_column_id(1, 0)

    def emoji_filter_func(self, model, iter, data):
        textMatch = True
        for s in self.filterEntry.get_text().split(' '):
            s = re.sub(r'(\\)$', '', s)
            # textMatch = textMatch and re.findall('\\b' + s, model[iter][1], re.IGNORECASE)
            textMatch = textMatch and re.findall(s, model[iter][1], re.IGNORECASE)
        return (True if len(self.selectedCategorys) == 0 else model[iter][3] in self.selectedCategorys) and textMatch

    # Score function to sort the searchresults
    def emoji_sort_func(self, model, a, b, user):
        score_a = 0
        score_b = 0
        if self.filterEntry.get_text() != '':
            for s in self.filterEntry.get_text().split(' '):
                s = re.sub(r'(\\)$', '', s)
                matches = re.findall('\\b\\S*?' + s + '\\S*?\\b', model[a][1], re.IGNORECASE)
                for m in matches:
                    start = m.find(s)
                    end = len(m) - len(s) - start
                    score_a += start + end
                score_a /= len(matches)
                matches = re.findall('\\b\\S*?' + s + '\\S*?\\b', model[b][1], re.IGNORECASE)
                for m in matches:
                    start = m.find(s)
                    end = len(m) - len(s) - start
                    score_b += start + end
                score_b /= len(matches)
            return score_a - score_b
        else:
            return 0

    def on_emoji_icon_selected(self, widget):
        if len(widget.get_selected_items()) == 1:
            sel = self.emojiSorter[widget.get_selected_items()[0].get_indices()[0]]
            if self.selectedEmoji != sel[0]:
                self.selectedEmoji = sel[0]
                print('Selected Emoji: {}; {}'.format(self.selectedEmoji, sel[1]))

class EmojiSelectorDlg(Gtk.Dialog):
    def __init__(self, parent, preselect=None, listview=False):
        Gtk.Dialog.__init__(self, "Emoji Selector", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(520, 500)

        self.emojiBox = EmojiSelectorBox(preselect=preselect)
        self.set_focus(self.emojiBox.filterEntry)

        box = self.get_content_area()
        box.pack_start(self.emojiBox, True, True, 2)

        self.connect('key-press-event', self.on_key_pressed)

        self.show_all()

    def on_key_pressed(self, widget, event):
        # print(event.keyval)
        if event.keyval == 0xff0d:
            self.response(Gtk.ResponseType.OK)


if __name__ == '__main__':
    print(os.path.dirname(os.path.abspath(__file__)))
    focusedWindow = check_output(['xdotool', 'getwindowfocus']).decode().strip()
    print('Found {} Emoji'.format(len(emojiStore)))
    win = EmojiSelectorDlg(None, preselect=None)
    # win.connect("delete-event", Gtk.main_quit)
    result = win.run()
    keyToSend = win.emojiBox.selectedEmoji
    if result == Gtk.ResponseType.OK and keyToSend != None:
        for k in keyToSend:
            cmd = ['xdotool', 'key', 'ctrl+shift+u'] + list(hex(k).replace('0x', '')) + ['Return']
            # print(['xdotool', 'key', 'ctrl+shift+u'] + list(hex(keyToSend).replace('0x', '')) + ['Return'])
            run(['xdotool', 'windowfocus', focusedWindow])
            # sleep(0.5)
            run(cmd)
            # run([u'xdotool', u'type', chr(keyToSend).encode('utf-8)')])
