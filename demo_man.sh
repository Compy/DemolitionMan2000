#!/bin/bash
export DISPLAY=:0
unflip
sudo rm -rf system.log
sudo python run.py

ecode=`cat EXIT_CODE`
if [ "$ecode" == "-13" ]; then
	echo "Restarting due to upgrade"
	sleep 2
	./demo_man.sh &
fi
