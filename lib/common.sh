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

# https://unix.stackexchange.com/a/426827
# converts HH:MM:SS.sss to fractional seconds
codes2seconds() (
    local hh=${1%%:*}
    local rest=${1#*:}
    local mm=${rest%%:*}
    local ss=${rest#*:}
    printf "%s" $(bc <<< "$hh * 60 * 60 + $mm * 60 + $ss")
)

# converts fractional seconds to HH:MM:SS.sss
seconds2codes() (
    local seconds=$1
    local hh=$(bc <<< "scale=0; $seconds / 3600")
    local remainder=$(bc <<< "$seconds % 3600")
    local mm=$(bc <<< "scale=0; $remainder / 60")
    local ss=$(bc <<< "$remainder % 60")
    printf "%02d:%02d:%06.3f" "$hh" "$mm" "$ss"
)

subtracttimes() (
    local t1sec=$(codes2seconds "$1")
    local t2sec=$(codes2seconds "$2")
    printf "%s" $(bc <<< "$t2sec - $t1sec")
)

# https://stackoverflow.com/a/17695543/4852536
function ask_yes_or_no() {
    read -p "$1 ([y]es or [N]o): "
    case $(echo $REPLY | tr '[A-Z]' '[a-z]') in
        y|yes) echo "yes" ;;
        *)     echo "no" ;;
    esac
}
