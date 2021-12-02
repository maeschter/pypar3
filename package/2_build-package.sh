#!/bin/sh
#Build deban package
#LastChangedDate: 2021.12.02

dpkg-deb -b ./pypar3

echo all done
echo Please press any key:
read key

