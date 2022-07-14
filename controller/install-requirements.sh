#!/bin/sh

input="./requirements.txt"
while read -r line
do
    arduino-cli lib install $line
done < "$input"
