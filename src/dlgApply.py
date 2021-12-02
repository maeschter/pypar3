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
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Gdk, Vte, GLib
from gi.repository.GdkPixbuf import Pixbuf
import os, signal, subprocess
import consts
from gettext import gettext as _


class DialogApply(Gtk.Dialog):
    def __init__(self, parent, cmd, workdir):
        super().__init__(self, transient_for=parent, modal=True)

        self.set_title(consts.appName)
        
        self.processPID        = -1  
        self.standAlone        = False
        self.cmd = cmd
        self.workDir = workdir

        self.set_size_request(consts.dialogApplyWidth, consts.dialogApplyHeight) #minimal size
        
        self.vte = Vte.Terminal()
        self.vte.set_hexpand(True)
        self.vte.set_vexpand(True)

        self.vscroll = Gtk.VScrollbar()
        self.vscroll.set_adjustment(self.vte.get_vadjustment())
       
        self.box = self.get_content_area()
        self.box.add(self.vte)
        
        # Button CLOSE
        self.add_button(_('Close'), Gtk.ResponseType.CLOSE)
        self.BtnClose = self.get_widget_for_response(Gtk.ResponseType.CLOSE)
        self.BtnClose.set_always_show_image(True)
        self.BtnClose.set_image(Gtk.Image.new_from_icon_name('dialog-close', Gtk.IconSize.BUTTON))
        self.BtnClose.set_margin_left(10)
        self.BtnClose.set_margin_right(10)

        # Signals -------------------------------
        self.connect('response', self.onResponse)
        self.connect('delete-event', self.onDelete)
        self.connect('key_release_event', self.onKeyRelease)
        #self.vte.connect("child-exited", self.onVteChildExited)


    # start process and display dialog -------------   
    # command line must be converted from list to string
    def show(self):
        # Running argsv as command doesn't work (file/dir not found error)
        # Run shell in terminal and when this process is established then run
        # par2 cmdline. This requires line feed (\n) at the end of the cmdline
        self.vte.spawn_async(
                    Vte.PtyFlags.DEFAULT,       # pty flags
                    self.workDir,               # working DIR
                    ['/bin/sh'],                # child’s command and argument vector
                    None,                       # list environmental variables (envv)
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,    # spawn flags
                    None,                       # child setup
                    None,
                    -1,                         # a timeout value in ms, -1 for the default timeout
                    None,                       # cancellable
                    self.vteChildCallback,      # callback
                    None                        # user data for callback
                            )
        self.show_all()


    # Child process started ---------------------
    # this receives the pid of the shell, not of par2
    # the cmd line get send to the shell for running the par2 tool
    def vteChildCallback(self, terminal, pid, error, userData):
        self.processPID = pid
        if pid == -1:
            print('dlgApply process error', error.args, error.message)
        else:
            # run par2: feed_child() has a bug so use deprecated feed_child_binary()
            argsv = ' '.join(self.cmd)
            self.vte.feed_child_binary(bytes(argsv,'utf8'))
            #print('dlgApply process id', pid)
            self.vte.set_input_enabled(False)
            #self.vte.watch_child(pid)


    # Child process finishd ---------------------
    # This signals the terminal window has been closed
#    def onVteChildExited(self, terminal, status):
#        self.processPID = -1
        

    # button CLOSE ------------------------------
    def onResponse(self, dialog, respId):
        # Close dialog, kill running process softly
        if respId == Gtk.ResponseType.CLOSE:
            #print('dlgApply button close')
            self.closeWindow()

    # key release: ctrl+q closes the dialog
    def onKeyRelease(self, widget, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_q:
            #print('onKeyRelease: ctrl+q')
            self.closeWindow()
            return False

    # button 'close window' (the X in upper right corner)
    def onDelete(self, widget, event):
        #print('dlgApply onDelete')
        self.closeWindow()
        return True

    # Close dialog, kill running process softly
    def closeWindow(self):
        #print('dlgApply closeWindow', self.processPID)
        if self.processPID != -1:
            os.kill(self.processPID, signal.SIGTERM)
        self.destroy()

        
# EOF -------------------------------------------------------------------------
