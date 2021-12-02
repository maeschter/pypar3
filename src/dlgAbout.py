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

from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import Pixbuf
import os.path
import consts
from gettext import gettext as _


class DialogAbout(Gtk.AboutDialog):
    def __init__(self, parent):
        super().__init__(self, transient_for=parent, flags=0)
        
        self.set_program_name (consts.appName)
        self.set_version (consts.appVersion)
        self.set_website (consts.appURL)
        
        self.set_comments(_('A graphical interface for the par2 command line utility.\n'
                            'PyPar3 is newly written using GTK3 but heavily inspired by François Ingelrest PyPar2.'))
        self.set_authors(['Maeschter',])
        self.add_credit_section(_('Thanks to'),
                                 [' François Ingelrest - Athropos@gmail.com',
                                  ' ',])
#        self.set_comments('PyPar3 is newly written using GTK3 but heavily inspired by François Ingelrest PyPar2')
        
        # Set logo
        if os.path.exists(consts.fileImgAbout):
            self.set_logo(Pixbuf.new_from_file(consts.fileImgAbout))

        # Display licence information
        self.set_license('This program is free software under the terms of the GNU General Public License,\n'
                        'either version 3 of the License, or (at your option) any later version.\n'
                        'For details see the GNU General Public License <http://www.gnu.org/licenses/>.')

        # Load the licence text from disk if possible
#        if os.path.exists(consts.fileLicense):
#            self.set_license(open(consts.fileLicense).read())
#            self.set_wrap_license(True)

        # Signals -------------------------------
        self.connect('key_release_event', self.onKeyRelease)


    # key release: ctrl+q closes the dialog
    def onKeyRelease(self, widget, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_q:
            #print('onKeyRelease: ctrl+q')
            self.destroy()
        return False
     
    # Display dialog ----------------------------        
    def show(self):
        self.run()
        self.destroy()
        
# EOF -------------------------------------------------------------------------
