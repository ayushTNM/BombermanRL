#!/bin/zsh

for DIM in 5 6 7 8 9 10
do
    # python3 menu.py -h
    python3 menu.py -d$DIM -b-1 -C8 -w18 -r10 -e100 -A0.05 -E0.01 -N14 -o plot$DIM
done
