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
import cpuinfo

parser = argparse.ArgumentParser(description='experiment')
parser.add_argument('samples', type=str, nargs='+',
                    help='A set of sample clips that ffmpeg can transcode')
parser.add_argument('--report-directory', dest='report_dir', type=str, required=True,
                    help='Location to output report data')
parser.add_argument('--screenshot-frequency', dest='screenshot_frequency', type=int, default=10,
                    help='How many seconds between screenshots in the sample files (default: 10)')
parser.add_argument('--compress-screenshots', dest='screenshot_compression', action='store_true',
                    help='When set, optipng will be run with argument `-o2` for 38 percent smaller PNG files with no data loss')
args = parser.parse_args()

'''
tests:
- libx265, crf 24-28, presets ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
    ffmpeg -i clip_1.mkv -c:v libx265 -crf 24 -preset slow -c:a copy out.mkv
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

def experiment_libx265(source_file, crf, preset, writer):
    # ffmpeg -i clip_1.mkv -c:v libx265 -crf 24 -preset slow -c:a copy out.mkv
    src_name, src_ext = os.path.splitext(source_file)
    src_bn = os.path.basename(src_name)

    temp_name = os.path.join(report_dir, 'libx265', f'{src_bn}___temp___{src_ext}')
    # %06d
    screenshots_format = f'{src_bn}___%05dpos_{preset}_crf{crf}.png' # clip_1___00012pos_superfast_crf22.png 

    start_time = time()
    cmd = f'ffpb -i {source_file} -c:v libx265 -crf {crf} -preset {preset} -c:a copy {temp_name}'
    subprocess.run(cmd, shell=True)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    elapsed_time = time() - start_time
    output_size = os.path.getsize(temp_name)
    original_size = os.path.getsize(source_file)
    # source_file, encoder, cpu_info, gpu_info, crf_value, preset, cq_value, encode_time, encode_size, original_size, command_used
    writer.writerow([source_file, 'libx265', cpu_brand, gpu_name, crf, preset, None, elapsed_time, output_size, original_size, cmd])
    # write screenshots for every 4 seconds of video
    # ffmpeg -i clip_1.mkv -vf fps=0.5 "output%06d.png"
    subprocess.run(f'ffpb -i {temp_name} -vf fps={1/args.screenshot_frequency} {os.path.join(report_dir, "libx265", screenshots_format)}', shell=True)
    os.remove(temp_name)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    optimize_pngs(os.path.join(report_dir, 'libx265'), f'{src_bn}*_{preset}_crf{crf}.png')

def experiment_hevc_nvenc(source_file, cq, writer):
    # ffmpeg -i clip_1.mkv -c:v hevc_nvenc -rc:v vbr_hq -cq:v 0 -b:v 100000k -maxrate:v 100000k -c:a copy out.mkv
    src_name, src_ext = os.path.splitext(source_file)
    src_bn = os.path.basename(src_name)

    temp_name = os.path.join(report_dir, 'hevc_nvenc', f'{src_bn}___temp___{src_ext}')
    # %06d
    screenshots_format = f'{src_bn}___%05dpos_cq{cq}.png'

    start_time = time()
    cmd = f'ffpb -i {source_file} -c:v hevc_nvenc -rc:v vbr_hq -cq:v {cq} -b:v 100000k -maxrate:v 100000k -c:a copy {temp_name}'
    subprocess.run(cmd, shell=True)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    elapsed_time = time() - start_time
    output_size = os.path.getsize(temp_name)
    original_size = os.path.getsize(source_file)
    # source_file, encoder, gpu_info, crf_value, preset, cq_value, encode_time, encode_size, original_size, command_used
    writer.writerow([source_file, 'hevc_nvenc', None, gpu_name, None, None, cq, elapsed_time, output_size, original_size, cmd])
    # write screenshots for every 4 seconds of video
    # ffmpeg -i clip_1.mkv -vf fps=0.5 "output%06d.png"
    subprocess.run(f'ffpb -i {temp_name} -vf fps={1/args.screenshot_frequency} {os.path.join(report_dir, "hevc_nvenc", screenshots_format)}', shell=True)
    os.remove(temp_name)
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
    #subprocess.run(f'find {os.path.join(report_dir, "hevc_nvenc")} -name "{src_bn}*_cq{cq}.png" -exec optipng -silent {{}} \\;', shell=True)
    optimize_pngs(os.path.join(report_dir, 'hevc_nvenc'), f'{src_bn}*_cq{cq}.png')

def optimize_pngs(path, mask):
    output = subprocess.check_output(['find', path, '-name', mask])
    pngs = output.decode('utf-8').split('\n')
    pngs = sorted(pngs)
    for pic in tqdm(pngs, desc='Optimizing screenshot PNGs on disk (lossless)', unit='file', position=0):
        subprocess.run(['optipng', ('-o2' if args.screenshot_compression else '-o0'), '-silent', pic])
    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line

# get GPU info
gpu_name = GPUtil.getGPUs()[0].name if (len(GPUtil.getGPUs()) > 0) else 'indeterminate'
cpu_brand = cpuinfo.get_cpu_info()['brand']

# convert to absolute path
samples = [os.path.abspath(item) for item in args.samples]
report_dir = os.path.abspath(args.report_dir)

# generate folder scaffold
folder_scaffold(os.path.abspath(args.report_dir))

# libx265
libx265 = dict()
libx265['crf_range'] = range(27,28)
libx265['presets'] = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
libx265['dir'] = os.path.join(report_dir, 'libx265')

# hevc_nvenc
hevc_nvenc = dict()
hevc_nvenc['cq_range'] = range(0,51)
hevc_nvenc['dir'] = os.path.join(report_dir, 'hevc_nvenc')

# for every sample
for src in tqdm(samples, desc='Source sample files', unit='file', position=3):
    with open(os.path.join(report_dir, f'{os.path.basename(src)}.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['source_file', 'encoder', 'cpu_info', 'gpu_info', 'crf_value', 'preset', 'cq_value', 'encode_time', 'encode_size', 'original_size', 'command_used'])
        
        # GPU experiment first
        for cq in tqdm(hevc_nvenc['cq_range'], desc='Testing hevc_nvenc -cq <int> (constant quality factor)', unit='experiment', position=2):
            continue
            experiment_hevc_nvenc(src, cq, writer)
        sys.stdout.write("\033[F") #back to previous line
        sys.stdout.write("\033[K") #clear line
        # CPU experiment next
        for preset in tqdm(libx265['presets'], desc='Testing libx265 -preset <name> (fast, slow, etc)', unit='preset', position=2):
            for crf in tqdm(libx265['crf_range'], desc='Testing libx265 -crf <int> (constant rate factor)', unit='experiment', position=1):
                experiment_libx265(src, crf, preset, writer)
            sys.stdout.write("\033[F") #back to previous line
            sys.stdout.write("\033[K") #clear line

exit()