#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: G.Trauth
# LastChange: 2021-12-28
# Created: 2021-12-25
#
# This program is free software under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# For details see the GNU General Public License <http://www.gnu.org/licenses/>.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.

# The function of this class is nearby identical to a simple Gtk.FileChooserButton but
# there's one sgnificant difference caused by the snap package:
# It is recommended to use the file chooser portal instead of the home and removable-media
# interfaces. The portal is supported since the gnome-3-34 extension.
# The portal works with hidden files and folders in the home directory. If a user chooses
# a hidden file, the portal will give your application access to it. The home interface
# does not give your app access to hidden files and folders in the home directory for
# security reasons. Note that the home interface does give access to hidden files and
# folders elsewhere, just not in the home directory itself.
# The portal works with removable-media out of the box.
# The disadvantage is: Files are fuse-mounted to /run/user/<uid>/doc/<hash>/ in order to
# give your application access to it. So the path your application sees is different from
# the path a user chose, even though both are the same file.
# This remounted file never gives us the correct dir path to the other par-files we need
# to check/repair.

import  gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gettext import gettext as _
import os.path
import consts


# Box with text entry and button for selecting a par file, supports drag'n'drop
class FileSelect(Gtk.Box):
    def __init__(self, parent, config):
        super().__init__()

        self.parent = parent
        self.conf = config
        self.dropType = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags.OTHER_APP , 0)

        self.set_can_focus(True)
        self.set_tooltip_text(_('Select a par2 file for checking or repairing.'))
        
        self.entry = Gtk.Entry()
        self.entry.set_editable(False)
        self.entry.set_margin_left(5)
        self.entry.set_margin_bottom(5)
        self.entry.drag_dest_set(Gtk.DestDefaults.ALL,[self.dropType],Gdk.DragAction.COPY)  # make drop destination
        
        self.button = Gtk.Button()
        #self.button.set_label(_('Select'))
        self.button.set_image(Gtk.Image.new_from_icon_name('document-open', Gtk.IconSize.BUTTON))

        self.button.set_alignment(0.5, 0.5)
        self.button.set_margin_left(5)
        self.button.set_margin_right(5)
        self.button.set_margin_bottom(5)
        
        self.pack_start(self.entry, True, True, 0)
        self.pack_start(self.button, False, True, 0)

        # filter *.par2 and *.PAR2 foe par file dialog
        self.filter = Gtk.FileFilter()
        self.filter.add_pattern(''.join(['*', consts.parFileExts[0]]))
        self.filter.add_pattern(''.join(['*', consts.parFileExts[1]]))


        self.entry.connect('drag-motion',        self.onDragMotion)
        self.entry.connect('drag-data-received', self.onDragData)
        self.button.connect('clicked',           self.onButtonParFile)


    # drag 'n drop ------------------------------
    # drag motion over entry: accept uris only, refuse rest
    # context: [Gdk.Atom.intern("x-special/gnome-icon-list", False),
    # Gdk.Atom.intern("text/uri-list", False), Gdk.Atom.intern("UTF8_STRING", False),
    # Gdk.Atom.intern("COMPOUND_TEXT", False), Gdk.Atom.intern("TEXT", False),
    # Gdk.Atom.intern("STRING", False), Gdk.Atom.intern("text/plain;charset=utf-8", False),
    # Gdk.Atom.intern("text/plain", False)]
    def onDragMotion(self, widget, context, x, y, time):
        t = self.entry.drag_dest_find_target(context, self.drag_dest_get_target_list()).name()
        if t == self.dropType.target:
            Gdk.drag_status(context, Gdk.DragAction.COPY, time)
            return True
        else:
            self.drag_unhighlight()
            Gdk.drag_status(context, 0, time)
            return  False

    # drop data on entry
    # dragMotion accepted uris as data and refused other
    def onDragData(self, widget, context, x, y, data, info, time):
        uris = data.get_uris()
        if uris != None:
            s = uris[0].replace('file://', '')
            self.conf.local['workDir'], self.conf.local['pathParFile'] = s.rsplit('/', 1)
        else:
            self.conf.local['pathParFile'] = ''
            self.conf.local['workDir'] = ''

        self.entry.set_text(self.conf.local['pathParFile'])
        #print('on drop par2 file:', self.conf.local['workDir'], self.conf.local['pathParFile'])
        self.grab_focus()
        self.show_all()

        
    # Notebook ntbAction par file chooser button clicked
    def onButtonParFile(self, w):
        result = self.fileDialog()
        if result is not None:
            #split in pathname, filename
            self.conf.local['workDir'], self.conf.local['pathParFile'] = result.rsplit('/', 1)
        else:
            self.conf.local['pathParFile'] = ''
            self.conf.local['workDir'] = ''

        self.entry.set_text(self.conf.local['pathParFile'])
        #print('button open file', self.conf.local['workDir'], self.conf.local['pathParFile'])


    # Dialog for par file -----------------------------------
    def fileDialog(self):
        result = None
        dialog = Gtk.FileChooserDialog(title = _('Choose par2 file'),
                                        parent = self.parent,
                                        action = Gtk.FileChooserAction.OPEN,
                                        select_multiple = False,
                                        filter = self.filter
                                        )
        dialog.add_buttons( Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OPEN, Gtk.ResponseType.OK )
        dialog.set_current_folder(consts.dirUsr)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = dialog.get_filenames()[0]
        dialog.destroy()
        return result
    

# EOF -------------------------------------------------------------------------
