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

#import xml.etree.ElementTree as et
import xml.dom.minidom as mido
from gettext import gettext as _
import os.path
import consts


class Config():

    def __init__(self):

        # parameter values (from/to config file)
        # this contains after startup the content of config file and
        # actual values during program run
        self.params =  {
                        'spnMemoryUsage'     : 16,
                        'spnBlockCount'      : 1,
                        'spnBlockSize'       : 1,
                        'spnRedundancyLevel' : 5,
                        'spnRedundancyCount' : 100,
                        'spnParFilesCount'   : 7,
                        'spnFirstBlock'      : 0,
                        'chkUniformFileSize' : False,
                        'radGrpCheck'        : 'radBtnCheckRepair',
                        'radGrpBlock'        : 'radBtnBlockCount',
                        'radGrpRedundancy'   : 'radBtnRedundancyCount',
                        'radGrpParity'       : 'radBtnParityCount',
                       }

        self.local =   {
                        'workDir'           : '',
                        'pathParFile'       : '',
                        'chkExtendedParams' : False
                        }

        self.readConfigFile()


    # set value 'value' for key 'name' when dict contains the key
    def setParameter(self, name, value):
        #print('config setParam', name, value)
        if name in self.params:
            self.params[name] = value
        else:
            raise KeyError(_('config: key or value error'))


    # read value for key 'name' when dict contains the key
    def getParameter(self, name):
        #print('getParam', name, self.params.get(name))
        if name in self.params:
            return self.params.get(name)
        else:
            raise KeyError(_('config: key or value error'))


    # set default parameters in dict 'params'
    def setDefault(self):
        for key in list(consts.defaultParams):
            self.setParameter(key, consts.defaultParams[key])


    # Read config file. Check access as considered in python library reference     
    def readConfigFile(self):
        try:
            fp = open(consts.fileConfig)
        except (OSError) as ex:
            self.setDefault()            # set default values on access restrictions
        else:
            root = mido.parse(fp).documentElement
            # Check file version
            if root.hasAttribute('version') and (int(root.getAttribute('version')) == consts.configVersion):
                for elem in root.getElementsByTagName('param'):
                    name  = elem.getAttribute('name')
                    value = self.cast(elem.getAttribute('value'), elem.getAttribute('type'))
                    self.setParameter(name, value)
                    #print(name, ' : ', value)
            else:
                self.setDefault()            # set default values on wrong version
                    

    # The file will always be generated newly
    def writeConfigFile(self):
        try:
            # create document and set root node
            doc  = mido.Document()
            root = doc.createElement('params')
            root.setAttribute('version', str(consts.configVersion))
            doc.appendChild(root)
            
            # Write parameters to the xml tree
            for name in self.params.keys():
                child = doc.createElement('param')
                value = self.params[name]
                child.setAttribute('name', name)
                child.setAttribute('value', str(value))
                child.setAttribute('type', self.getType(value))
                root.appendChild(child)
            # Save the document to the disk
            with open(consts.fileConfig, "w") as f:
                f.write(doc.toprettyxml())
            #print(doc.toprettyxml())
        except (KeyError,ValueError,) as ex:
            print('config write: key or value error:', ex.args[0])


    # Type conversions --------------------------
    # Return a String with the type of value
    def getType(self, value) :
        for type in consts.types.keys():
            if isinstance(value, type):
                return consts.types[type]
        raise TypeError(_('config: type unsupported'))

    # Return value, casted into related type
    def cast(self, value, type) :
        if type == 'bool' :
            return value == 'True'
        elif type == 'int' :
            return int(value)
        elif type == 'str' :
            return str(value)
        raise TypeError(_('config: type unsupported'))   
    


# EOF -------------------------------------------------------------------------
