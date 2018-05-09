#!/bin/bash

depth=${1:-1}
path=${2:-/dev/null}

mysleep=15

echo "$depth $$ $PPID" >> $path

if [ $depth -ne 0 ]; then
    "$0" $(($depth -1)) "$path" &
fi

sleep $mysleep
