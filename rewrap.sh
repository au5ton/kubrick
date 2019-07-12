#!/bin/bash
DIR=$(dirname "$0") && . $DIR/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext>"
    exit
fi

time ffmpeg -i "$1" -c:v copy -c:a aac -ac 2 "$2"