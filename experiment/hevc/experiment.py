#!/usr/bin/env python3

import os
import csv
import sys
import argparse
import threading
import subprocess
from time import time

from tqdm import tqdm
from halo import Halo
import GPUtil

parser = argparse.ArgumentParser(description='experiment')
parser.add_argument('samples', type=str, nargs='+',
                    help='A set of sample clips that ffmpeg can transcode')
parser.add_argument('--report', dest='report_dir', type=str, required=True,
                    help='Location to output report data')
parser.add_argument('--screenfreq', dest='screenshot_frequency', type=int, default=4,
                    help='How many seconds between screenshots in the sample files (default: 4 seconds)')
args = parser.parse_args()

'''
tests:
- libx265, crf 24-28, presets ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
- hevc_nvenc, 
    -cq:v [0,51]
    ffmpeg -i clip_1.mkv -c:v hevc_nvenc -rc:v vbr_hq -cq:v 0 -b:v 100000k -maxrate:v 100000k -c:a copy out.mkv
- frames
    ffmpeg -i clip_1.mkv -vf fps=0.5 "output%06d.png"
report/
    _source/
    clip_1.mkv.csv
    clip_2.mkv.csv
    libx265/
        clip_1.mkv.dir/
            # for every 2 seconds of footage, for every crf in crf_range, for every preset
            clip_1_00012pos_crf24_preset-ultrafast.png
            clip_1_00012pos_crf24_preset-superfast.png
            ...
            clip_1_00012pos_crf22_preset-ultrafast.png
            clip_1_00012pos_crf22_preset-superfast.png
            ...
            clip_1_00012pos_crf22_preset-ultrafast.png
            clip_1_00012pos_crf22_preset-superfast.png
    hevc_nvenc/
        # for every 2 seconds of footage, for every cq in cr_range
        clip_1_00012pos_cq0.png
        clip_1_00012pos_cq1.png
        clip_1_00012pos_cq1.png
        ...

csv header format:

    source_file, encoder, gpu_info, crf_value, preset, cq_value, encode_time, encode_size
'''

def folder_scaffold(report_dir):
    folders = [
        report_dir,
        os.path.join(report_dir, '_source'),
        os.path.join(report_dir, 'libx265'),
        os.path.join(report_dir, 'hevc_nvenc')
    ]
    for f in folders:
        if not os.path.isfile(f) and not os.path.isdir(f):
            os.mkdir(f)
        else:
            print(f'couldnt create directory: {f}')
            exit(1)

#def experiment_libx265(source_file, crf, preset):
    #

def experiment_hevc_nvenc(source_file, cq, writer):
    # ffmpeg -i clip_1.mkv -c:v hevc_nvenc -rc:v vbr_hq -cq:v 0 -b:v 100000k -maxrate:v 100000k -c:a copy out.mkv
    src_name, src_ext = os.path.splitext(source_file)
    src_bn = os.path.basename(src_name)

    temp_name = os.path.join(report_dir, 'hevc_nvenc', f'{src_bn}___temp___{src_ext}')
    # %06d
    screenshots_format = f'{src_bn}___%05dpos_cq{cq}.webp' # clip_1___00012pos_cq0.png 

    start_time = time()
    subprocess.run(f'ffpb -i {source_file} -c:v hevc_nvenc -rc:v vbr_hq -cq:v {cq} -b:v 100000k -maxrate:v 100000k -c:a copy {temp_name}', shell=True)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    elapsed_time = time() - start_time
    output_size = os.path.getsize(temp_name)
    # source_file, encoder, gpu_info, crf_value, preset, cq_value, encode_time, encode_size
    writer.writerow([src_bn, 'hevc_nvenc', gpu_name, None, None, cq, elapsed_time, output_size])
    # write screenshots for every 4 seconds of video
    # ffmpeg -i clip_1.mkv -vf fps=0.5 "output%06d.png"
    subprocess.run(f'ffpb -i {temp_name} -vf fps={1/args.screenshot_frequency} {os.path.join(report_dir, "hevc_nvenc", screenshots_format)}', shell=True)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    os.remove(temp_name)

# get GPU info
gpu_name = GPUtil.getGPUs()[0].name if (len(GPUtil.getGPUs()) > 0) else 'indeterminate'

# convert to absolute path
samples = [os.path.abspath(item) for item in args.samples]
report_dir = os.path.abspath(args.report_dir)

# generate folder scaffold
folder_scaffold(os.path.abspath(args.report_dir))

# libx265
libx265 = dict()
libx265['crf_range'] = range(24,28)
libx265['presets'] = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
libx265['dir'] = os.path.join(report_dir, 'libx265')

# hevc_nvenc
hevc_nvenc = dict()
hevc_nvenc['cq_range'] = range(0,51)
hevc_nvenc['dir'] = os.path.join(report_dir, 'hevc_nvenc')

# for every sample
for src in tqdm(samples, desc='Source sample files', unit='files', position=2):
    with open(os.path.join(report_dir, f'{os.path.basename(src)}.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['source_file', 'encoder', 'gpu_info', 'crf_value', 'preset', 'cq_value', 'encode_time', 'encode_size'])
        
        # GPU experiment first
        for cq in tqdm(hevc_nvenc['cq_range'], desc='Testing hevc_nvenc -cq <float> (constant quality factor)', unit='experiments', position=1):
            experiment_hevc_nvenc(src, cq, writer)

exit()