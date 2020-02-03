#!/bin/bash
DIR=`cd $(dirname "$0"); cd ..; pwd` && . $DIR/lib/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <timecode> <output.ext>"
    echo -e "\tffmpeg video filters require transcoding!"
    exit
fi

time ffmpeg -ss "$2" -i "$1" -vframes 1 -q:v 2 "$3"