#!/bin/zsh

greeting="Welcome"
user=$(whoami)
day=$(date +%D)

echo "$greeting back $user! Today is $day."