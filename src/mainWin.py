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
from gi.repository import Gtk, Gdk
from gettext import gettext as _
import os.path, sys
import consts, config, fileBox, fileSelect, dlgAbout, dlgApply


class Window(Gtk.ApplicationWindow):
    def __init__(self, app, args):
        super(Window, self).__init__(title="consts.appName", application=app)

        self.app = app
        self.conf = config.Config()
        self.defaultSize = (-1, -1)
        
        # Builder object for window components-------
        self.builder = Gtk.Builder().new_from_file(os.path.join(consts.dirRes, 'win-main.glade'))
        self.builder.set_translation_domain(consts.appNameShort)
        self.mainWin = self.builder.get_object('appwin')

        # Tab CHECK with file entry and file select button
        self.selectFrame = self.builder.get_object('ntbActionTab0Frm0')
        self.chooser = fileSelect.FileSelect(self, self.conf)
        self.selectFrame.add(self.chooser)

        # Tab CREATE with scrollable file listbox
        self.scrollWin = self.builder.get_object('ntbActionTab1ScrollWin')
        self.fileBox = fileBox.FileBox(self, self.conf)
        self.scrollWin.add(self.fileBox)

        # Icons ---------------------------------
        self.builder.get_object('appBtnInfo').set_image(Gtk.Image.new_from_icon_name('help-about', Gtk.IconSize.BUTTON))
        self.builder.get_object('appBtnQuit').set_image(Gtk.Image.new_from_icon_name('application-exit', Gtk.IconSize.BUTTON))
        self.builder.get_object('appBtnApply').set_image(Gtk.Image.new_from_icon_name('dialog-ok', Gtk.IconSize.BUTTON))
        self.builder.get_object('appBtnSetDefault').set_image(Gtk.Image.new_from_icon_name('view-restore', Gtk.IconSize.BUTTON))

        # Signals, handlers ---------------------
        handlers = {
            'onAppDestroy'           : self.onAppDestroy,
            'onAppKeyReleaseEvent'   : self.onKeyRelease,
            'onButtonAbout'          : self.onButtonAbout,
            'onButtonQuit'           : self.onButtonQuit,
            'onButtonApply'          : self.onButtonApply,
            'onButtonDefault'        : self.onButtonDefault,
            'onNtbSwitchPage'        : self.onNtbSwitchPage,
            'onRadBtnToggled'        : self.onRadButtons,
            'onSpinBtnChanged'       : self.onSpinButtons,
            'onChkButtonToggled'     : self.onChkButtons
                    }
        self.builder.connect_signals(handlers)

        # set configuration parameters to widgets
        # Before configuring the widgets all signal handlers must be established
        self.configureWidgets()
        
        # run dlgApply in repair/verify mode when command-line contains a par2 file
        #print('run cmdlind args', args)
        if (len(args) > 1):
            if args[1].endswith(consts.parFileExts):
                print('run cmdlind arg', args[1])
                self.conf.setParameter('pathParFile', args[1])
                term = dlgApply.DialogApply(self)
                # prepare commandline and run
                cmd = self.composeCmdLine()
                term.show(cmd)

        
    # show all windgets -------------------------
    # triggers configure-event with real window size -> defaultSize
    def show(self):
        self.mainWin.show_all()

    # error message on incomplete command for CREATE
    def errorMessage(self):
        messDlg = Gtk.MessageDialog(
                            transient_for=self,
                            flags=0,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text = _('File to protect missing'))
        messDlg.format_secondary_text(_('Please select a least one file to protect'))
        messDlg.run()
        messDlg.destroy()

    # Events ------------------------------------
    # App key release: ctrl+q closes the app
    def onKeyRelease(self, widget, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_q:
            #print('onKeyRelease: ctrl+q')
            self.conf.writeConfigFile()
            self.app.quit()
        return False

    # Close application: destroy window or button quit
    def onAppDestroy(self, widget):
        self.conf.writeConfigFile()
        self.app.quit()

    def onButtonQuit(self, button):
        self.conf.writeConfigFile()
        self.app.quit()
    
    # About dialog ------------------------------
    def onButtonAbout(self, button):
        #print('button About clicked')
        dlg = dlgAbout.DialogAbout(self)
        dlg.show()

    # Apply dialog ------------------------------
    # Perform action CHECK, VERIFY or CREATE
    # The appropriate action is detemined by the command line
    def onButtonApply(self, button):
        # prepare commandline
        cmd = self.composeCmdLine()
        if cmd is not None:
            wd = self.conf.local['workDir']
            print('onButtonApply workdir', wd)
            output = dlgApply.DialogApply(self, cmd, wd)
            output.show()

    # Set default values ------------------------
    def onButtonDefault(self, button):
        self.conf.setDefault()
        self.configureWidgets()


    # Notebook tab clicked ----------------------
    # active tab CHECK in ntbAction ->  pageCheck: hide tabs 1-4 in ntbParams 
    # active tab CREATE in ntbAction -> pageCreate: show tabs 1-4 in ntbParams 
    def onNtbSwitchPage(self, notebook, page, page_num):
        #print('onNtbSwitchPage', notebook.get_name(), page.get_name())
        pages = [1,2,3,4]
        if notebook.get_name() == 'ntbAction':
            if page.get_name() == 'pageCreate':
                self.builder.get_object('chkExtendedParams').set_sensitive(True)
                self.fileBox.grab_focus()
                self.fileBox.removeAllFiles()
                for i in pages:
                    self.builder.get_object('ntbParams').get_nth_page(i).show()
            else:
                self.builder.get_object('chkExtendedParams').set_sensitive(False)
                self.builder.get_object('chkExtendedParams').set_active(False)
                for i in pages:
                    self.builder.get_object('ntbParams').get_nth_page(i).hide()
            
    
    # Each radioButton group with n buttons delivers n signals on toggle!
    def onRadButtons(self, button):
        if button.get_active():
            name = button.get_name()
            for grp in list(consts.radioButtonGroups):
                if name in consts.radioButtonGroups[grp]:
                    #print('onRadActionToggled', grp, name)
                    self.conf.setParameter(grp, name)
            toEnable, toDisable = consts.radioActions[name]
            #print('to enable', toEnable, 'to disable', toDisable)
            for strObj in toEnable:
                self.builder.get_object(strObj).set_sensitive(True)
            for strObj in toDisable:
                self.builder.get_object(strObj).set_sensitive(False)
                if strObj == 'chkUniformFileSize':
                    self.builder.get_object('chkUniformFileSize').set_active(False)


    # Notebook ntbParams spin button Memory
    def onSpinButtons(self, button):
        self.conf.setParameter(button.get_name(), int(button.get_value()))
        #print('spin button', button.get_name(), self.conf.getParameter(button.get_name()))


    # Button 'chkUniformFileSize' will be saved in config file
    # Button 'chkExtendedParams' will be used locally only
    def onChkButtons(self, button):
        name = button.get_name()
        if name == 'chkUniformFileSize':
            self.conf.setParameter(name, str(button.get_active()))
            #print('check button', button.get_name(), self.conf.getParameter(button.get_name()))
        if name == 'chkExtendedParams':
            self.conf.local[name] = str(button.get_active())
                        
    
    # write configuration parameters to widgets
    def configureWidgets(self):
        for spnBtn in consts.spinButtons:
            #print('spinButtons', builder.get_object(spnBtn).get_name(), int(self.conf.getParameter(spnBtn)))
            self.builder.get_object(spnBtn).set_value(self.conf.getParameter(spnBtn))

        # the dict config.params contains the names of the radiobuttons to be set
        # the radiobutton groups are keys in dict consts.radioButtonGroups
        for grp in list(consts.radioButtonGroups):
            #print('radioButtons', grp, builder.get_object(self.conf.getParameter(grp).get_name()))
            self.builder.get_object(self.conf.getParameter(grp)).set_active(True)

        # the boolean value for set_active must be derived from comparisation
        for chkBtn in consts.checkButtons:
            #print('checkButtons', builder.get_object(chkBtn).get_name(), self.conf.getParameter(chkBtn))
            self.builder.get_object(chkBtn).set_active(self.conf.getParameter(chkBtn) == 'True')


    # Conmpose command line as list for repair/verify and for create
    # consider restrictions for particular parameter combinations
    def composeCmdLine(self):
        cmdLine =''
        mem = '-m' + str(self.conf.getParameter('spnMemoryUsage'))
        extended = []
        if self.conf.local['chkExtendedParams']:
            if 'radBtnBlockCount' == self.conf.getParameter('radGrpBlock'):
                blk = '-b' + str(self.conf.getParameter('spnBlockCount'))
                extended.append(blk)
            if 'radBtnBlockSize' == self.conf.getParameter('radGrpBlock'):
                bls = '-s' + str(self.conf.getParameter('spnBlockSize'))
                extended.append(bls)

            if 'radBtnRedundancyLevel' == self.conf.getParameter('radGrpRedundancy'):
                rel = '-r' + str(self.conf.getParameter('spnRedundancyLevel'))
                extended.append(rel)
            if 'radBtnRedundancyCount' == self.conf.getParameter('radGrpRedundancy'):
                rec = '-c' + str(self.conf.getParameter('spnRedundancyCount'))
                extended.append(rec)

            if 'radBtnParitySize' == self.conf.getParameter('radGrpParity'):
                extended.append('-l')
            if 'radBtnParityCount' == self.conf.getParameter('radGrpParity'):
                pfc = '-n' + str(self.conf.getParameter('spnParFilesCount'))
                extended.append(pfc)
                if self.builder.get_object('chkUniformFileSize').get_active():
                    extended.append('-u')
            extended.append('-f' + str(self.conf.getParameter('spnFirstBlock')))
        
        # repair or verify
        if (consts.ntbActionPages[self.builder.get_object('ntbAction').get_current_page()] == 'CHECK'):
            #check or verify
            check = consts.cmdCheck[self.conf.getParameter('radGrpCheck')]
            parfile = self.conf.local['pathParFile']
            if parfile != '':
                cmdLine = ['par2', check, mem]
                cmdLine.append(''.join(['"',parfile,'"']))
            else:
                cmdLine = None
                self.errorMessage()
        else:
            # create
            cmdLine = ['par2 c', mem,] + extended
            if self.fileBox.getParFileName() != '':
                cmdLine.append(self.fileBox.getParFileName())

                if self.fileBox.getFilesToProtect() != '':
                    cmdLine.append(''.join([ '-- ', self.fileBox.getFilesToProtect()]))
                else:
                    cmdLine = None
                    self.errorMessage()
            else:
                cmdLine = None
                self.errorMessage()

        cmdLine.append('\n')                # feed the terminal with commad line
        return cmdLine

    #set notebook ACTION page CHECK (> disable pages 1-4 of notebook PARAMS)
    def setNotebookPages(self):
        self.builder.get_object("ntbAction").set_current_page(1)
        self.builder.get_object("ntbAction").set_current_page(0)


# EOF -------------------------------------------------------------------------
