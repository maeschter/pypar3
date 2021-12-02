#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: G.Trauth
# LastChange: 2021-12-02
# Created: 2021-07-04
#
# This program is free software under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# For details see the GNU General Public License <http://www.gnu.org/licenses/>.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.

import  gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gettext import gettext as _
import os.path, urllib.parse
import consts


class DataListBoxRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.add(Gtk.Label(label=data))

    def getData(self):
        return  self.data


class FileBox(Gtk.ListBox):
    def __init__(self, parent, config):
        super().__init__()

        self.parent = parent
        self.conf = config
        self.dropType = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags.OTHER_APP , 0)
        # for test only
        #self.dropType1 = Gtk.TargetEntry.new('TEXT', Gtk.TargetFlags.OTHER_APP , 0)

        self.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.set_activate_on_single_click(False)    # otherwise multiple selection fails
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_can_focus(True)
        self.drag_dest_set(Gtk.DestDefaults.ALL,[self.dropType],Gdk.DragAction.COPY)  # make drop destination
        self.set_tooltip_text(_('Files to protect.\n'
                                'Note: all files in the listbox will be protected,\n'
                                'regardless if they are marked or not.\n'
                                'You also may set a name (no file extension) for the par2 files.\n'
                                'If not, a name will be created by PyPar2.\n'
                                'All files must be enclosed in the same directory.'))

        self.connect('enter-notify-event', self.onNotifyEnter)
        self.connect('button-press-event', self.onButtonPress)
        self.connect('key-release-event',  self.onKeyRelease)
        self.connect('drag-motion',        self.onDragMotion)
        self.connect('drag-data-received', self.onDragData)

        # Builder object for popOver ------------
        self.builder = Gtk.Builder().new_from_file(os.path.join(consts.dirRes, 'pop-over.glade'))
        self.popOver = self.builder.get_object('popOver')
        self.popOver.set_relative_to(self.parent.scrollWin)
        self.popOver.set_modal(False)
        self.popOver.set_constrain_to(Gtk.PopoverConstraint.NONE)
        self.popOver.set_position(Gtk.PositionType.BOTTOM)
        
        self.entry = self.builder.get_object('popEntry')
        self.entry.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY) #refuse drop

        # popover signals
        handler = { 'onPopBtnClicked' : self.onPopBtnClicked,
                    'onPopEntryEnter' : self.onPopEntryEnter
                    }
        self.builder.connect_signals(handler)


    # drag 'n drop ------------------------------
    # drag motion over listbox: accept uris only, refuse rest
    # context: [Gdk.Atom.intern("x-special/gnome-icon-list", False),
    # Gdk.Atom.intern("text/uri-list", False), Gdk.Atom.intern("UTF8_STRING", False),
    # Gdk.Atom.intern("COMPOUND_TEXT", False), Gdk.Atom.intern("TEXT", False),
    # Gdk.Atom.intern("STRING", False), Gdk.Atom.intern("text/plain;charset=utf-8", False),
    # Gdk.Atom.intern("text/plain", False)]
    def onDragMotion(self, widget, context, x, y, time):
        t = self.drag_dest_find_target(context, self.drag_dest_get_target_list()).name()
        if t == self.dropType.target:
            Gdk.drag_status(context, Gdk.DragAction.COPY, time)
            return True
        else:
            self.drag_unhighlight()
            Gdk.drag_status(context, 0, time)
            return  False

    # drop data on listbox
    # dragMotion accepted uris as data and refused other
    def onDragData(self, widget, context, x, y, data, info, time):
        uris = data.get_uris()
        if uris != None:
            for f in uris:
                s = urllib.parse.unquote(f.replace('file://', ''))
                self.add(DataListBoxRow(s))
                self.conf.local['workDir'] = os.path.dirname(s)
        self.grab_focus()
        self.show_all()
        
        
    # getter and setter -------------------------
    # return par2 filename either from text entry or from first file in listbox
    def getParFileName(self):
        text = ''
        if self.get_row_at_y (0) is not None:
            fn = str(self.get_row_at_y (0).data)
            bd = os.path.dirname(fn)
        # prepend base dir to filename and append extension
        if self.entry.get_text() != '':
            t = self.entry.get_text()
            if not t.lower().endswith('.par2'):
                text = ''.join(['"', bd, '/', t, '.par2"'])
            else:
                text = ''.join(['"', bd, '/', t, '"'])
        else:
            # append extension to filename
            text = ''.join(['"', fn, '.par2"'])
        return  text

    # return list of files from listbox
    def getFilesToProtect(self):
        toProtect = ''
        chld = self.get_children()          #get list of all DataListBoxRow widgets
        if len(chld) > 0:
            for c in chld:
                fn = str(c.getData())
                toProtect = ''.join([toProtect, '"', fn, '" '])
        #print('getFilesToProtect', toProtect)
        return toProtect
        
    def getWorkDir(self):
        wd = self.conf.local['workDir']
        #print('workdir', wd)
        return wd


    # Dialogs -----------------------------------
    def fileDialog(self, files=True):
        result = None
        if files:
            dialog = Gtk.FileChooserDialog( title = 'Choose files',
                                        parent = self.parent,
                                        action = Gtk.FileChooserAction.OPEN
                                        )
            dialog.set_select_multiple(True)
        else:
            dialog = Gtk.FileChooserDialog( title = 'Choose directory',
                                        parent = self.parent,
                                        action = Gtk.FileChooserAction.SELECT_FOLDER 
                                        )
            dialog.set_select_multiple(False)

        dialog.add_buttons( Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = dialog.get_filenames()
        dialog.destroy()
        return result


    # Control popover and list ------------------
    # open when mouse pointer enters the list box
    # close when clicked in listbox or a button clicked,
    # delete selected files on key 'Del'
    def onNotifyEnter(self, widget, event):
        self.popOver.show()
        return True

    # return False otherwise the selection of files won't work
    def onButtonPress(self, widget, event):
        self.popOver.hide()
        self.grab_focus()
        return False

    def onKeyRelease(self, widget, event):
        if (event.keyval == Gdk.KEY_Delete and widget == self):
            self.removeSelectedFiles()
        return False

    # Buttons in popover ------------------------
    def onPopBtnClicked(self, button):
        name = button.get_name()
        self.popOver.hide()
        if name == 'popBtn1':
            self.addFilesToList()
        elif name == 'popBtn2':
            self.addDirToList(button)
        elif name == 'popBtn3':
            self.removeSelectedFiles()
        elif name == 'popBtn4':
            self.removeAllFiles()
        else:
            print('popover button not found')

    # add files to list -------------------------
    def addFilesToList(self):
        files = self.fileDialog(files=True)
        if files != None:
            for f in files:
                self.add(DataListBoxRow(f))
                self.conf.local['workDir'] = os.path.dirname(f)
        self.grab_focus()
        self.show_all()

    # add files of a dir to list ----------------
    def addDirToList(self, button):
        result = self.fileDialog(files=False)
        if result != None:
            dir = result[0]
            content = os.scandir(dir)
            for f in content:
                if f.is_file():
                    self.add(DataListBoxRow(os.path.join(dir, f.name)))
            self.conf.local['workDir'] = dir
        self.grab_focus()
        self.show_all()

    # remove selected rows in ListBox -----------
    def removeSelectedFiles(self):
        wdg = self.get_children()
        for cld in wdg:         
            if cld.is_selected():
                self.remove(cld)
        wdg = self.get_children()           # clear workDir on empty listbox
        if len(wdg) < 1:
            self.conf.local['workDir'] = ''

    # remove all rows in ListBox ----------------
    def removeAllFiles(self):
        self.select_all()
        self.removeSelectedFiles()

    # text entry --------------------------------
    def onPopEntryEnter(self, entry):
        self.popOver.hide()


# EOF -------------------------------------------------------------------------
