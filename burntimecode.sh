#!/bin/bash
DIR=$(dirname "$0") && . $DIR/common.sh
if ishelp $1; then
    echo "$0 <input.ext> <output.ext>"
    echo -e "\tffmpeg video filters require transcoding!"
    exit
fi

fontcheck
HEIGHT=`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1 "$1" | grep 'height=' | cut -d "=" -f 2- -`
font_size=`expr $HEIGHT / 14`
timecode_rate=`ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate "$1"`

# echo $HEIGHT
# echo $font_size
# exit


ffmpeg -i "$1" -c:a copy -vf drawtext="fontfile=$KUBRICK_FONTPATH:timecode='00\\:00\\:00\\:00':fontsize=$font_size:fontcolor=0xFFFFFF:box=0:boxcolor=0xFFFFFF:rate=$timecode_rate:x=(w-text_w)/2:y=h/1.2" "$2"


# ffmpeg -i input_file -vf drawtext="fontfile=font_path:fontsize=font_size:timecode=starting_timecode:fontcolor=font_colour:box=1:boxcolor=box_colour:rate=timecode_rate:x=(w-text_w)/2:y=h/1.2" output_file