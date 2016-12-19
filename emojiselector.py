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

        self.selectedEmoji = preselect
        self.selectedCategorys = []

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        for cat in emojiCategorys:
            btn = Gtk.ToggleButton(cat)
            btn.connect('clicked', self.on_category_button_clicked, cat)
            hbox.pack_start(btn, True, True, 0)

        self.pack_start(hbox, False, True, 0)

        self.filterEntry = Gtk.Entry()
        self.filterEntry.connect('changed', self.on_filter_entry_changed)

        self.pack_start(self.filterEntry, False, True, 0)

        self.categoryFilter = emojiStore.filter_new()
        self.categoryFilter.set_visible_func(self.category_filter_func)

        emojiListView = Gtk.IconView.new_with_model(self.categoryFilter)
        emojiListView.set_pixbuf_column(2)
        emojiListView.set_selection_mode(Gtk.SelectionMode.BROWSE)
        for i, value in enumerate(self.categoryFilter):
            if value[0] == preselect:
                emojiListView.select_path(Gtk.TreePath.new_from_indices([i]))
                emojiListView.scroll_to_path(Gtk.TreePath.new_from_indices([i]), True, 0.5, 0.5)
        emojiListView.connect('selection-changed', self.on_emoji_icon_selected)

        scroll = Gtk.ScrolledWindow()
        scroll.add(emojiListView)

        self.pack_start(scroll, True, True, 0)

    def on_category_button_clicked(self, widget, category):
        if widget.get_active():
            if not category in self.selectedCategorys:
                self.selectedCategorys.append(category)
        else:
            if category in self.selectedCategorys:
                self.selectedCategorys.remove(category)
        self.categoryFilter.refilter()
        # print(self.selectedCategorys)

    def on_filter_entry_changed(self, widget):
        # print(self.filterEntry.get_text().split(' '))
        self.categoryFilter.refilter()

    def category_filter_func(self, model, iter, data):
        textMatch = True
        for s in self.filterEntry.get_text().split(' '):
            s = re.sub(r'(\\)$', '', s)
            textMatch = textMatch and re.findall('\\b' + s, model[iter][1], re.IGNORECASE)
        return (True if len(self.selectedCategorys) == 0 else model[iter][3] in self.selectedCategorys) and textMatch

    def on_emoji_icon_selected(self, widget):
        if len(widget.get_selected_items()) == 1:
            sel = self.categoryFilter[widget.get_selected_items()[0].get_indices()[0]]
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
        self.show_all()


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
