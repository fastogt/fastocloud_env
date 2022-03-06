#!/usr/bin/env python3

import os
import subprocess
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
           'testsrcbin',
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
           'opusparse',
           'tee',
           'flvmux',
           'mp4mux',
           'qtmux',
           'mpegtsmux',
           'webmmux',
           'filesink',
           'rtpmux',
           'rtpmp2tpay',
           'rtph264pay',
           'rtph265pay',
           'rtpmp4apay',
           'rtpac3pay',
           'rtppcmupay',
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
           'fakesrc',
           'wpevideosrc',
           'wpesrc',
           'cefsrc',
           'imagefreeze',
           'capsfilter',
           'audioconvert',
           'rgvolume',
           'volume',
           'faac',
           'opusenc',
           'voaacenc',
           'audioresample',
           'lamemp3enc',
           'videoconvert',
           'avdeinterlace',
           'deinterlace',
           'videoflip',
           'aspectratiocrop',
           'udpsink',
           'rtspclientsink',
           'tcpserversink',
           'rtmpsink',
           'rtmp2sink',
           'httpsink',
           'hlssink',
           'hlssink2',
           'souphttpsrc',
           'dvbsrc',
           'videoscale',
           'videorate',
           'multifilesink',
           'nvh264enc',
           'nvh265enc',
           'msdkh264enc',
           'vp8enc',
           'vp9enc',
           'x264enc',
           'x265enc',
           'mpeg2enc',
           'eavcenc',
           'openh264enc',
           'udpsrc',
           'rtmpsrc',
           'rtmp2src',
           'rtspsrc',
           'rtpsrc',
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
           'compositor',
           'alpha',
           'interleave',
           'deinterleave',
           'textoverlay',
           'videocrop',
           'spectrum',
           'level',
           'hlsdemux',
           'decklinkvideosink',
           'decklinkaudiosink',
           'interlace',
           'autovideoconvert',

           'glvideomixer',
           'glalpha',

           'cudascale',
           'cudaconvert',
           'cudadownload',
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
           'input-selector',
           'kvssink',
           's3sink',
           'webrtcbin']

PLUGINS_ML = [
    'tinyyolov2',
    'tinyyolov3',
    'detectionoverlay',
    'nvinfer',
    'nvtracker',
    'nvvideoconvert',
    'nvstreammux',
    'nvv4l2h264enc',
    'nvv4l2h265enc',
    'nvv4l2vp8enc',
    'nvv4l2vp9enc',
    'nvdsosd',
    'dsfastogt',
    'fastogtbackground',
    'fastogtaudio'
]


def check_plugins():
    env = os.environ
    env['LD_LIBRARY_PATH'] = '$LD_LIBRARY_PATH:/usr/local/TensorRT-7.2.2.3/lib:/usr/local/VideoFX/lib/'
    env['GST_PLUGIN_PATH'] = '$GST_PLUGIN_PATH:/usr/local/lib/gstreamer-1.0/'
    with open(os.devnull, 'w') as devnull:
        print('\nPlugins for FastoCloud COM/PRO:')
        for plugin in PLUGINS:
            try:
                subprocess.check_output(['gst-inspect-1.0', plugin], env=env, stderr=devnull)
                print_success('Check plugin {0}, success return code: {1}'.format(plugin, 0))
            except CalledProcessError as e:
                print_error('Check plugin {0}, failed return code: {1}'.format(plugin, e.returncode))

        print('\nPlugins for FastoCloud ML:')
        for plugin in PLUGINS_ML:
            try:
                subprocess.check_output(['gst-inspect-1.0', plugin], env=env, stderr=devnull)
                print_success('Check plugin {0}, success return code: {1}'.format(plugin, 0))
            except CalledProcessError as e:
                print_error('Check plugin {0}, failed return code: {1}'.format(plugin, e.returncode))


if __name__ == "__main__":
    check_plugins()
