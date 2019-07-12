#!/bin/bash
DIR=$(dirname "$0") && . $DIR/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext> <start> <end>"
    echo -e "\tTime unit syntax: HOURS:MM:SS.MILLISECONDS"
    exit
fi

time ffmpeg -i "$1" -ss "$3" -to "$4" -c copy -map 0 "$2"