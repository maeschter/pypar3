#!/bin/sh
#Update deban package for build
#LastChangedDate: 2021.12.02
#The script must be in the dir <package>

#Print Working Directory: 
echo start package update
cd pypar3
pwd

echo
# translations
rm -f -v usr/share/locale/*.*
cp -a -v ../../pypar3/locale/de/LC_MESSAGES/*.mo  usr/share/locale/de/LC_MESSAGES

echo
# Application
rm -f -v usr/share/pypar3/pix/*.*
rm -f -v usr/share/pypar3/res/*.*
rm -f -v usr/share/pypar3/src/*.*

cp -a -v ../../pypar3/pix/*.png           usr/share/pypar3/pix
cp -a -v ../../pypar3/res/*.glade         usr/share/pypar3/res
cp -a -v ../../pypar3/src/*.py            usr/share/pypar3/src

echo
echo all done
echo Please press any key:
read key

