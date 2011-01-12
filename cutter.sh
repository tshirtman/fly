#!/usr/bin env sh
for i in {0..29}; do convert lvl1_foreground.png -crop 1000x0+29000x480 lvl1_foreground_29.png; done
