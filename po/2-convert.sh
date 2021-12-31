#!/bin/sh
# Convert the PO files into "Message Object" files (extension .mo)
# in the appropriate localeDir
# This file must be in pypar3/po
# 2021.12.31

msgfmt -v de_DE.po  --output-file=../locale/de/LC_MESSAGES/pypar3.mo


echo Finished, please press a key
read k
