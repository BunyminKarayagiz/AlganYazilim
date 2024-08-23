#!/bin/bash

echo "Provided IP: $1"

rpicam-vid -t 0 --inline -o "udp://$1:5555" --nopreview
