#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: G.Trauth
# LastChange: 2021-12-21
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
from gi.repository import Gtk, Gio, GLib
import sys, locale, gettext
import mainWin, consts


# Application ----------------------------------------------------------------
class Application(Gtk.Application):
    def __init__(self, *args):
        super().__init__(*args, application_id = consts.appID,
                         flags = Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

    # 1. startup application --------------------
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # gettext.textdomain doesn't work with the GTK3 glade files
        locale.bindtextdomain(consts.appNameShort, consts.dirLoc)
        locale.textdomain(consts.appNameShort)
#        gettext.textdomain(consts.appNameShort)
#        gettext.bindtextdomain(consts.appNameShort, consts.dirLoc)

    # 2. Gio.Application command line -----------
    # the command line supports one par file for check/repair
    def do_command_line(self, cmdl):
        args = cmdl.get_arguments()
        #start application window !!
        self.do_activate(args)
        return 0

    # 3. application window ---------------------
    def do_activate(self, args):
        self.window = mainWin.Window(self, args)
        self.window.show()
        
        #set notebook ACTION page CHECK (> disable pages 1-4 of notebook PARAMS)
        # notebook already must be shown 
        self.window.setNotebookPages()

# Main program ------------------------------------------------------------------
def main():
    app = Application()
    app.run(sys.argv)
    

if __name__ == "__main__":
    main()
    
# EOF -------------------------------------------------------------------------

