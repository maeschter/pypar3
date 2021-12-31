#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: G.Trauth
# LastChange: 2021-12-31
# Created: 2021-12-21
#
# This program is free software under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# For details see the GNU General Public License <http://www.gnu.org/licenses/>.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# Directory structure of source project
# /home/..../app/ executables (not used)
#           /locale/ translations
#           /src/ python
#           /res/ icons, glade

# Directory structure in SNAP package
# $SNAP/bin/ executables
#      /share/locale/ translations
#      /share/pypyar3/src/ python
#                    /res/ icons, glade

import os.path

# Application
appVersion    = '0.1.0'
appURL        = 'https://github.com/maeschter/pypar3'
appID         = 'com.github.maeschter.pypar3'
appName       = 'PyPar3'
appNameShort  = 'pypar3'
configVersion = 1
parFileExts   = ('.par2', '.PAR2')

dialogApplyWidth  = 600
dialogApplyHeight = 500

# Directories SNAP / source project
# SNAP: dirUsr = /home/user/snap/pypar3/x1, project: dirUsr = /home/user/pypar3
dirUsr = os.path.expanduser('~')
l = dirUsr.split('/')
dirHome = os.path.join('/', l[1], l[2])
dirCfg = os.path.join(dirUsr, '.config/', appNameShort)

dirSrc = os.path.join(os.path.dirname(__file__))        # expecting .../src
if dirSrc.endswith('src/'):
    dirSrc = dirSrc.rstrip('/')

if dirSrc.startswith('/home'):
    dirPrj = dirSrc.rstrip('/src')
    dirRes = os.path.join(dirPrj, 'res')
    dirLoc = os.path.join(dirPrj, 'locale')
else:
    dirPrj = dirSrc.rstrip('pypar3/src')
    dirRes = os.path.join(dirPrj, 'pypar3/res')
    dirLoc = os.path.join(dirPrj, 'locale')

print('Home dir ', dirHome)
print('Project dir ', dirPrj)
#print('dirCfg ', dirCfg)
#print('dirRes ', dirRes)
#print('dirLoc ', dirLoc)

# Files
fileConfig   = os.path.join(dirCfg, appNameShort+'.xml')
fileImgIcon  = os.path.join(dirRes, 'pypar3.png')

# Create the configuration directory if needed
if not os.path.isdir(dirCfg):
    os.mkdir(dirCfg)


# app default values (mostly for creation of par files)
defaultParams = {
            'spnMemoryUsage'      : 16,
            'spnBlockCount'       : 1,
            'spnBlockSize'        : 1,
            'spnRedundancyLevel'  : 5,
            'spnRedundancyCount'  : 100,
            'spnParFilesCount'    : 7,
            'spnFirstBlock'       : 0,
            'chkUniformFileSize'  : False,
            'radGrpCheck'         : 'radBtnCheckVerify',
            'radGrpBlock'         : 'radBtnBlockCount',
            'radGrpRedundancy'    : 'radBtnRedundancyCount',
            'radGrpParity'        : 'radBtnParityCount' 
                }


ntbActionPages = ['CHECK', 'CREATE']
spinButtons  = ['spnMemoryUsage', 'spnBlockCount', 'spnBlockSize', 'spnRedundancyLevel',
                'spnRedundancyCount', 'spnParFilesCount', 'spnFirstBlock']
checkButtons = ['chkUniformFileSize']
# radioButton groups and associated actions
# groups only are helpers to simplfy reading/writing the config file and default values
radioButtonGroups =  {
        'radGrpCheck'      : ('radBtnCheckRepair', 'radBtnCheckVerify'),
        'radGrpBlock'      : ('radBtnBlockDynamic', 'radBtnBlockCount', 'radBtnBlockSize'),
        'radGrpRedundancy' : ('radBtnRedundancyLevel' , 'radBtnRedundancyCount'),
        'radGrpParity'     : ('radBtnParitySize', 'radBtnParityCount')
                    }

# cmd line restrictions (see MAN page)
# Block‐Count -b<n> disables Block‐Size -s<n> and related spinButtons
# Redundancy Level (%) -r<n> disables Recovery block count -c<n> and related spinButtons
# Uniform recovery file sizes -u disables Limit size of recovery files -l
# Number of recovery files -n<n> disables Limit size of recovery files -l
# The dict contains two lists for each radiobutton: the first list contains the spinButtons to enable
# the second list contains the spinButtons to disable
radioActions = {'radBtnCheckRepair'     : ([],                                         []                                        ),
                'radBtnCheckVerify'     : ([],                                         []                                        ),
                'radBtnBlockDynamic'    : ([],                                         ['spnBlockCount', 'spnBlockSize' ]        ),
                'radBtnBlockCount'      : (['spnBlockCount'],                          ['spnBlockSize']                          ),
                'radBtnBlockSize'       : (['spnBlockSize'],                           ['spnBlockCount']                         ),
                'radBtnRedundancyLevel' : (['spnRedundancyLevel'],                     ['spnRedundancyCount']                    ),
                'radBtnRedundancyCount' : (['spnRedundancyCount'],                     ['spnRedundancyLevel']                    ),
                'radBtnParitySize'      : ([],                                         ['spnParFilesCount', 'chkUniformFileSize']),
                'radBtnParityCount'     : (['spnParFilesCount', 'chkUniformFileSize'], []                                        )
                }

# Type conversions on reading/writing the xml-config-file
# 'bool' type must be placed *before* 'int' type, otherwise booleans are detected as integers
types = {bool : 'bool', int : 'int', str : 'str'}

# cmd line options for par2
cmdCheck = {'radBtnCheckRepair': 'r', 'radBtnCheckVerify': 'v'}


# EOF -------------------------------------------------------------------------
