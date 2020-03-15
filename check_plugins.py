#!/usr/bin/env python3

import subprocess
import os
from subprocess import CalledProcessError

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'


def print_success(msg):
    print(OKGREEN + msg + ENDC)


def print_error(msg):
    print(FAIL + msg + ENDC)


PLUGINS = ['decodebin',
           'fakesink',
           'testsink',
           'videotestsrc',
           'audiotestsrc',
           'ximagesrc',
           'autovideosink',
           'autoaudiosink',
           'queue',
           'queue2',
           'h264parse',
           'h265parse',
           'mpegvideoparse',
           'aacparse',
           'ac3parse',
           'mpegaudioparse',
           'rawaudioparse',
           'tee',
           'flvmux',
           'mpegtsmux',
           'filesink',
           'rtpmux',
           'rtpmp2tpay',
           'rtph264pay',
           'rtph265pay',
           'rtpmp4apay',
           'rtpac3pay',
           'rtpmp2tdepay',
           'rtph264depay',
           'rtph265depay',
           'rtpmp4adepay',
           'rtpac3depay',
           'v4l2src',
           'splitmuxsink',
           'alsasrc',
           'multifilesrc',
           'appsrc',
           'filesrc',
           'imagefreeze',
           'capsfilter',
           'audioconvert',
           'rgvolume',
           'volume',
           'faac',
           'voaacenc',
           'audioresample',
           'lamemp3enc',
           'videoconvert',
           'avdeinterlace',
           'deinterlace',
           'aspectratiocrop',
           'udpsink',
           'tcpserversink',
           'rtmpsink',
           'hlssink',
           'souphttpsrc',
           'videoscale',
           'videorate',
           'multifilesink',
           'nvh264enc',
           'nvh265enc',
           'msdkh264enc',
           'x264enc',
           'x265enc',
           'mpeg2enc',
           'eavcenc',
           'openh264enc',
           'udpsrc',
           'rtmpsrc',
           'rtspsrc',
           'tcpserversrc',
           'vaapih264enc',
           'vaapimpeg2enc',
           'vaapidecodebin',
           'vaapipostproc',
           'gdkpixbufoverlay',
           'rsvgoverlay',
           'videobox',
           'videomixer',
           'audiomixer',
           'interleave',
           'deinterleave',
           'cairooverlay',
           'textoverlay',
           'videocrop',
           'spectrum',
           'level',
           'hlsdemux',
           'decklinkvideosink',
           'decklinkaudiosink',
           'interlace',
           'autovideoconvert',
           'tsparse',
           'avdec_h264',
           'tsdemux',
           'avdec_ac3',
           'avdec_ac3_fixed',
           'avdec_aac',
           'avdec_aac_fixed',
           'souphttpclientsink',
           'mfxh264enc',
           'mfxvpp',
           'mfxh264dec',
           'srtsrc',
           'srtsink',
           'tinyyolov2',
           'tinyyolov3',
           'detectionoverlay',
           'kvssink']


def check_plugins():
    with open(os.devnull, 'w') as devnull:
        for plugin in PLUGINS:
            try:
                subprocess.check_output(['gst-inspect-1.0', plugin], stderr=devnull)
                print_success('Check plugin {0}, success return code: {1}'.format(plugin, 0))
            except CalledProcessError as e:
                print_error('Check plugin {0}, failed return code: {1}'.format(plugin, e.returncode))


if __name__ == "__main__":
    check_plugins()
