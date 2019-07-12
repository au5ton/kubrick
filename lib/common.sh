#!/bin/bash

ishelp() {
    if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        return 0 # true
    else
        return 1 # false
    fi
    #justbashthings
}

export KUBRICK_DIR=`cd $(dirname "$0"); cd ..; pwd`
export KUBRICK_FONT="IBMPlexMono-Regular.ttf"
export KUBRICK_FONTPATH="$KUBRICK_DIR/temp/$KUBRICK_FONT"
export KUBRICK_TEMPDIR="$KUBRICK_DIR/temp"
export KUBRICK_TOOLPATH="$KUBRICK_DIR/tool"

fontcheck() {
    if test -f "$KUBRICK_FONTPATH"; then
        return 0
    else
        $KUBRICK_DIR/lib/download_font.sh
        return 0
    fi
}