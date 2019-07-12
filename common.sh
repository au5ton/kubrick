#!/bin/bash

ishelp() {
    if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        return 0 # true
    else
        return 1 # false
    fi
    #justbashthings
}