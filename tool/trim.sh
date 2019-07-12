#!/bin/bash
DIR=`cd $(dirname "$0"); cd ..; pwd` && . $DIR/lib/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext> <start> <end> [--dirty]"
    echo -e "\tTime unit syntax: HOURS:MM:SS.MILLISECONDS"
    echo -e "\tMust specify all units, no abbreviations."
    echo -e "\tThe --dirty argument uses stream copying only."
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

if [ "$5" = "--dirty" ]; then
    # dirty trim
    time ffmpeg -ss "$preseek" -i "$1" -ss 00:00:01 -t "$duration" -c copy -map 0 "$2"
else
    # re-encode
    time ffmpeg -ss "$preseek" -i "$1" -ss 00:00:01 -t "$duration" -c:v libx264 -preset veryfast -crf 22 -c:a copy -c:s copy "$2"
fi

