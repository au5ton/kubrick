#!/bin/bash
cd $(dirname "$0")
mkdir -p ../temp
cd ../temp
wget -q --show-progress https://github.com/google/fonts/raw/master/ofl/ibmplexmono/IBMPlexMono-Regular.ttf