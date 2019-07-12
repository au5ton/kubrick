#!/bin/bash
DIR=`cd $(dirname "$0"); cd ..; pwd` && . $DIR/lib/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext>"
    echo -e "\tffmpeg video filters require transcoding!"
    exit
fi

fontcheck
HEIGHT=`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1 "$1" | grep 'height=' | cut -d "=" -f 2- -`
font_size=`expr $HEIGHT / 14`
timecode_rate=`ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate "$1"`

time ffmpeg -i "$1" -c:a copy -vf drawtext="fontfile=$KUBRICK_FONTPATH:timecode='00\\:00\\:00\\:00':fontsize=$font_size:fontcolor=0xFFFFFF:box=0:boxcolor=0xFFFFFF:rate=$timecode_rate:x=(w-text_w)/2:y=h/1.2" "$2"
