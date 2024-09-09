#!/bin/bash

echo "Provided IP: $1"

rpicam-vid -t 0 --inline -o "udp://$1:5555" --framerate 30 --width 640 --height 480 --nopreview
