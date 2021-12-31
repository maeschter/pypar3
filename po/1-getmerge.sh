#!/bin/sh
# Collect text for translations in pypar3.pot
# Merge changes into the language-specific PO files
# This file must be in pypar3/po
# 2021.12.30

echo get text
xgettext    -o pypar3.pot ../src/config.py
xgettext -j -o pypar3.pot ../src/consts.py
xgettext -j -o pypar3.pot ../src/dlgAbout.py
xgettext -j -o pypar3.pot ../src/dlgApply.py
xgettext -j -o pypar3.pot ../src/fileBox.py
xgettext -j -o pypar3.pot ../src/fileSelect.py
xgettext -j -o pypar3.pot ../src/mainWin.py
xgettext -j -o pypar3.pot ../src/pypar3.py

xgettext -j --keyword=translatable -o pypar3.pot ../res/win-main.glade
xgettext -j --keyword=translatable -o pypar3.pot ../res/pop-over.glade

echo merge into language-specific PO files
msgmerge --update de_DE.po pypar3.pot


echo Finished, please press a key
read k

