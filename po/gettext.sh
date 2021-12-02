#!/bin/sh
# Get text for translation
# This file must be in pypar3/po
# 2021.08.20

cd ..
echo
xgettext -j  -o ./po/pypar3.pot ./src/config.py
xgettext -j  -o ./po/pypar3.pot ./src/consts.py
xgettext -j  -o ./po/pypar3.pot ./src/dlgAbout.py
xgettext -j  -o ./po/pypar3.pot ./src/dlgApply.py
xgettext -j  -o ./po/pypar3.pot ./src/fileBox.py
xgettext -j  -o ./po/pypar3.pot ./src/mainWin.py
xgettext -j  -o ./po/pypar3.pot ./src/pypar3.py

xgettext -j --keyword=translatable -o ./po/pypar3.pot ./res/win-main.glade
xgettext -j --keyword=translatable -o ./po/pypar3.pot ./res/pop-over.glade

echo Finished - write pypar3.pot
echo please press a key
read k

