#!/bin/sh
echo "Copying directory contents to USB flash drive..."
#/Volumes/Untitled
if [ -d "/Volumes/PINBOX/pinbox_update" ]; then
	rm -rf /Volumes/PINBOX/pinbox_update/
fi
mkdir /Volumes/PINBOX/pinbox_update

if [ $# -eq 1 ]; then
	echo "Copying all assets and code..."
	cp -rf ../demo_man/* /Volumes/PINBOX/pinbox_update/
else
	rsync -av --exclude 'assets' . /Volumes/PINBOX/pinbox_update/
fi

echo "Unmounting USB flash drive"
diskutil unmount /Volumes/PINBOX
