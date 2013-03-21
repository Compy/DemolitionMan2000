#!/bin/bash
export DISPLAY=:0
unflip
sudo python run.py > system.log

ecode=`cat EXIT_CODE`
if [ "$ecode" == "-13" ]; then
	echo "Restarting due to upgrade"
	sleep 2
	./demo_man.sh &
fi
