#!/bin/bash

ishelp() {
    if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        return 0 # true
    else
        return 1 # false
    fi
    #justbashthings
}

export KUBRICK_DIR=$(dirname "$0")
export KUBRICK_FONT="IBMPlexMono-Regular.ttf"
export KUBRICK_FONTPATH="$KUBRICK_DIR/$KUBRICK_FONT"

fontcheck() {
    if test -f "$KUBRICK_FONTPATH"; then
        return 0
    else
        $KUBRICK_DIR/download_font.sh
        return 0
    fi
}