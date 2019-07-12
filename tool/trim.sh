#!/bin/bash
DIR=`cd $(dirname "$0"); cd ..; pwd` && . $DIR/lib/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext> <start> <end>"
    echo -e "\tTime unit syntax: HOURS:MM:SS.MILLISECONDS"
    echo -e "\tMust specify all units, no abbreviations."
    exit
fi

# start timecode in seconds
start=$(codes2seconds "$3")
# one second before the desired start time
preseek=$(bc <<< "$start - 1")
# duration of the clip
duration=$(subtracttimes "$3" "$4")
# convert seconds to code for -ss
preseek=$(seconds2codes "$preseek")

# old way
# time ffmpeg -i "$1" -ss "$3" -to "$4" -c copy -map 0 "$2"

# new way
time ffmpeg -ss "$preseek" -i "$1" -ss 00:01:00 -t "$duration" -c copy -map 0 "$2"