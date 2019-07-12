#!/bin/bash
DIR=`cd $(dirname "$0"); cd ..; pwd` && . $DIR/lib/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext>"
    exit
fi

time ffmpeg -i "$1" -c:a copy -vn "$2"