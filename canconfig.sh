#!/bin/bash -e

usage() {
	echo
	echo "usage: $0 <canif> [<device>] || clean"
	echo "   eg: $0 can0 /dev/ttyACM0"
	echo
	exit 1
}

if [ "$1" == "clean" ]; then
	pids=$(pidof slcand)
	if [ -n "$pids" ]; then
		sudo kill $pids
	fi
	exit 0
fi

canif=$1
devif=$2

if [ -z "$canif" ]; then
	usage
fi

chkcan=$(ip a | grep $canif:) || true
if [ -z "$chkcan" ]; then
	if [ -z "$devif" ]; then
		usage
	fi
	# -s5 bitrate is 250K
	sudo slcand -o -s5 $devif $canif
	sudo ip link set up $canif
fi
chkcan=$(ip a | grep $canif:) || true
if [ -n "$chkcan" ]; then
	echo $chkcan
else
	echo "$canif not configured.  Check the device name."
fi
