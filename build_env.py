#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil
import sys
from abc import ABCMeta, abstractmethod

from pyfastogt import system_info, build_utils, utils

from check_plugins import check_plugins

_file_path = os.path.dirname(os.path.abspath(__file__))

# Script for building environment on clean machine

if sys.version_info < (3, 8): # streamlink
    print('Tried to start script with an unsupported version of Python. build_env requires Python 3.8 or greater')
    sys.exit(1)

DEFAULT_HOSTNAME = "fastocloud.com"

GSTREAMER_SRC_ROOT = "https://gstreamer.freedesktop.org/src/"
GSTREAMER_ARCH_COMP = "xz"
GSTREAMER_ARCH_EXT = "tar." + GSTREAMER_ARCH_COMP

GST_PLUGINS_BASE_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_BASE_ARCH_COMP = "xz"
GST_PLUGINS_BASE_ARCH_EXT = "tar." + GST_PLUGINS_BASE_ARCH_COMP

GST_PLUGINS_GOOD_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_GOOD_ARCH_COMP = "xz"
GST_PLUGINS_GOOD_ARCH_EXT = "tar." + GST_PLUGINS_GOOD_ARCH_COMP

GST_PLUGINS_BAD_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_BAD_ARCH_COMP = 'xz'
GST_PLUGINS_BAD_ARCH_EXT = 'tar.' + GST_PLUGINS_BAD_ARCH_COMP

GST_PLUGINS_UGLY_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_UGLY_ARCH_COMP = 'xz'
GST_PLUGINS_UGLY_ARCH_EXT = 'tar.' + GST_PLUGINS_UGLY_ARCH_COMP

GST_LIBAV_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_LIBAV_ARCH_COMP = 'xz'
GST_LIBAV_ARCH_EXT = 'tar.' + GST_LIBAV_ARCH_COMP

GST_RTSP_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_RTSP_ARCH_COMP = 'xz'
GST_RTSP_ARCH_EXT = 'tar.' + GST_RTSP_ARCH_COMP

GST_RUST_PLUGINS = 'https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs'

AWS_SDK_URL = 'https://github.com/aws/aws-sdk-cpp'
AWS_S3_URL = 'https://github.com/amzn/amazon-s3-gst-plugin'
GST_NICE_URL = 'https://gitlab.freedesktop.org/libnice/libnice'

NDI_URL = 'https://github.com/Palakis/obs-ndi'
FAAC_URL = 'https://github.com/knik0/faac/archive/1_30.tar.gz'
OPENH264_URL = 'https://github.com/cisco/openh264'
LIBVA_URL = 'https://github.com/intel/libva'
LIBVA_UTILS_URL = 'https://github.com/intel/libva-utils'
INTEL_VAAPI_DRIVER_URL = 'https://github.com/intel/intel-vaapi-driver'
GMM_LIB_URL = 'https://github.com/intel/gmmlib'
INTEL_MEDIA_DRIVER_URL = 'https://github.com/intel/media-driver'
MEDIA_SDK_URL = 'https://github.com/Intel-Media-SDK/MediaSDK'
GSTREAMER_MFX_URL = 'https://github.com/fastogt/gstreamer-media-SDK'
OPENCV_URL = 'https://github.com/opencv/opencv'

WPE_URL = 'https://wpewebkit.org/releases'
WPE_ARCH_COMP = 'xz'
WPE_ARCH_EXT = 'tar.' + WPE_ARCH_COMP

WPE_BACKEND_URL = 'https://wpewebkit.org/releases'
WPE_BACKEND_ARCH_COMP = 'xz'
WPE_BACKEND_ARCH_EXT = 'tar.' + WPE_BACKEND_ARCH_COMP

WPE_WEBKIT_URL = 'https://wpewebkit.org/releases'
WPE_WEBKIT_ARCH_COMP = 'xz'
WPE_WEBKIT_ARCH_EXT = 'tar.' + WPE_WEBKIT_ARCH_COMP

SRT_SRC_URL = 'https://github.com/Haivision/srt/archive'
SRT_ARCH_COMP = 'gz'
SRT_ARCH_EXT = 'tar.' + SRT_ARCH_COMP


class OperationSystem(metaclass=ABCMeta):
    @abstractmethod
    def get_required_exec(self) -> list:
        pass

    @abstractmethod
    def get_build_exec(self) -> list:
        pass

    @abstractmethod
    def get_build_gst_exec(self) -> list:
        pass

    @abstractmethod
    def get_nvidia_libs(self) -> list:
        pass

    @abstractmethod
    def get_wpe_libs(self) -> list:
        pass

    @abstractmethod
    def get_mongo_libs(self) -> list:
        pass

    @abstractmethod
    def get_gst_build_libs(self):
        pass

    def get_gst_repo_libs(self):
        pass


class Debian(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'g++', 'make', 'ninja-build', 'python3-pip', 'python3-dev']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'cmake', 'libtool', 'pkg-config', 'libudev-dev', 'libssl-dev', 'unifdef']

    def get_build_gst_exec(self) -> list:
        return ['gettext', 'bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return ['nvidia-cuda-dev', 'nvidia-cuda-toolkit', 'libnvidia-ml-dev']

    def get_wpe_libs(self) -> list:
        return ['libegl-dev', 'libegl1-mesa-dev', 'libxkbcommon-dev', 'libwayland-dev', 'libepoxy-dev', 'ruby',
                'libgcrypt20-dev', 'libwebp-dev', 'libxslt1-dev', 'libsystemd-dev', 'libcurl4-openssl-dev',
                'libgudev-1.0-dev', 'libgbm-dev', 'gperf', 'wayland-protocols']

    def get_mongo_libs(self) -> list:
        return ['libmongoc-dev']

    def get_gst_build_libs(self):
        return ['libmount-dev', 'libglib2.0-dev', 'glib-networking',
                'libdrm-dev', 'libproxy-dev', 'libpciaccess-dev', 'libxfixes-dev',
                'libblkid-dev', 'libsoup2.4-dev', 'libsoup-3.0-dev', 'libjpeg-dev',
                'librtmp-dev', 'libasound2-dev', 'libx264-dev', 'libx265-dev', 'libfaad-dev', 'libmp3lame-dev',
                'libvpx-dev',
                'libxcb-dri3-dev', # 'libx11-xcb-dev',
                'libopus-dev', 'libvo-aacenc-dev',
                'libgdk-pixbuf2.0-dev', 'libpango1.0-dev', 'librsvg2-dev', 'libpulse-dev',
                # 'freeglut3-dev', # 'libegl1-mesa-dev',
                'libsrtp2-dev', 'zlib1g-dev', 'libbz2-dev'
                # 'libffi-dev', 'libxrandr-dev', 'intltool', 'liborc-0.4-dev', 'libxml2-dev'
                ]  # libgstreamer-plugins-base1.0-dev

    def get_gst_repo_libs(self):
        return ['libgstreamer1.0-dev', 'libgstreamer-plugins-base1.0-dev',
                'libgstreamer-plugins-good1.0-dev', 'libgstreamer-plugins-bad1.0-dev', 'libgstrtspserver-1.0-dev',
                'gstreamer1.0-tools',
                'gstreamer1.0-plugins-base', 'gstreamer1.0-plugins-good', 'gstreamer1.0-plugins-bad',
                'gstreamer1.0-plugins-ugly', 'gstreamer1.0-libav', 'gstreamer1.0-nice', 'gstreamer1.0-rtsp']


class RedHat(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'gcc-c++', 'make', 'ninja-build', 'python3-pip', 'python3-devel']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig', 'libudev-devel', 'openssl-devel']

    def get_build_gst_exec(self) -> list:
        return ['gettext', 'bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return ['mongo-c-driver-devel']

    def get_gst_build_libs(self):
        return ['libmount-devel', 'glib2-devel', 'glib-networking',
                'libdrm-devel', 'libproxy-devel', 'libpciaccess-devel', 'libXfixes-devel',
                'librtmp-devel', 'libsoup-devel', 'libx264-devel', 'libx265-devel', 'alsa-lib-devel', 'lame-devel',
                'libvpx-devel',
                'libopus-devel', 'libvo-aacenc-devel',
                'libjpeg-turbo-devel', 'gdk-pixbuf2-devel', 'libpango-devel', 'librsvg2-dev', 'pulseaudio-libs-devel',
                'libsrtp2-devel', 'libxcb-devel', 'zlib-devel'  # 'libffi-devel', 'pcre-devel'
                ]

    def get_gst_repo_libs(self):
        return ['gstreamer1', 'gstreamer1-plugins-base',
                'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad-free', 'gstreamer1-plugins-ugly-free', 'gstreamer1-libav',
                'gstreamer1-nice', 'gstreamer1-rtsp-server']


class Arch(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'make', 'ninja', 'python3-pip', 'python3-dev']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig', 'udev', 'openssl']

    def get_build_gst_exec(self) -> list:
        return ['gettext', 'bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return ['libmongoc']

    def get_gst_build_libs(self) -> list:
        return ['libutil-linux', 'glibc', 'glib-networking',
                'libdrm', 'libproxy',
                'rtmpdump', 'libsoup', 'x264', 'x265', 'alsa-lib', 'lame', 'libjpeg', 'gdk-pixbuf2', 'vpx',
                'opus', 'ocaml-voaacenc',
                'srtp2', 'zlib'  # 'libffi', 'pcre'
                ]

    def get_gst_repo_libs(self):
        return ['gstreamer', 'gstreamer-plugins-base', 'gstreamer-plugins-good',
                'gstreamer-plugins-bad', 'gstreamer-plugins-ugly', 'gstreamer-libav', 'gstreamer-nice',
                'gstreamer-rtsp-server']


class FreeBSD(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'make', 'ninja', 'python3-pip', 'python3-devel', 'dbus']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconf', 'libudev-devd', 'openssl']

    def get_build_gst_exec(self) -> list:
        return ['gettext', 'bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return ['libmongoc']

    def get_gst_build_libs(self):
        return ['glib2-devel', 'glib-networking',
                'libdrm', 'libproxy',
                'librtmp', 'libsoup', 'libx264', 'libx265', 'alsa-lib', 'libjpeg-turbo', 'libopus', 'libvoaac',
                'libvpx',
                'libxcb', 'lsrtp2', 'lzlib', 'gdk-pixbuf2',  # 'libffi', 'pcre'
                ]

    def get_gst_repo_libs(self):
        return ['gstreamer1', 'gstreamer1-plugins-base', 'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad', 'gstreamer1-plugins-ugly', 'gstreamer1-libav', 'gstreamer1-nice',
                'gstreamer1-rtsp-server']


class Windows64(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'make', 'autoconf', 'automake', 'libtool',
                'mingw-w64-x86_64-yasm', 'mingw-w64-x86_64-nasm', 'mingw-w64-x86_64-gcc', 'mingw-w64-x86_64-ninja',
                'python3-pip']

    def get_build_exec(self) -> list:
        return []

    def get_build_gst_exec(self) -> list:
        return ['bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return []

    def get_gst_build_libs(self):
        return ['mingw-w64-x86_64-glib2', 'mingw-w64-x86_64-glib-networking']

    def get_gst_repo_libs(self):
        return ['mingw-w64-x86_64-gstreamer',
                'mingw-w64-x86_64-gst-plugins-base', 'mingw-w64-x86_64-gst-plugins-good',
                'mingw-w64-x86_64-gst-plugins-bad', 'mingw-w64-x86_64-gst-plugins-ugly', 'mingw-w64-x86_64-gst-libav',
                'mingw-w64-x86_64-libnice', 'mingw-w64-x86_64-gst-rtsp-server']


class Windows32(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'make', 'autoconf', 'automake', 'libtool',
                'mingw-w64-i686-yasm', 'mingw-w64-i686-nasm', 'mingw-w64-i686-gcc', 'mingw-w64-i686-ninja',
                'python3-pip']

    def get_build_exec(self) -> list:
        return []

    def get_build_gst_exec(self) -> list:
        return ['bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return []

    def get_gst_build_libs(self):
        return ['mingw-w64-i686-glib2', 'mingw-w64-i686-glib-networking']

    def get_gst_repo_libs(self):
        return ['mingw-w64-i686-gstreamer',
                'mingw-w64-i686-gst-plugins-base', 'mingw-w64-i686-gst-plugins-good',
                'mingw-w64-i686-gst-plugins-bad', 'mingw-w64-i686-gst-plugins-ugly', 'mingw-w64-i686-gst-libav',
                'mingw-w64-i686-libnice', 'mingw-w64-i686-gst-rtsp-server']


class MacOSX(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'make', 'ninja', 'python3-pip', 'python3-devel']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig']

    def get_build_gst_exec(self) -> list:
        return ['gettext', 'bison', 'flex']

    def get_nvidia_libs(self) -> list:
        return []

    def get_wpe_libs(self) -> list:
        return []

    def get_mongo_libs(self) -> list:
        return ['libmongo']

    def get_gst_build_libs(self):
        return ['glib2-devel', 'glib-networking']

    def get_gst_repo_libs(self):
        return ['gstreamer1', 'gstreamer1-plugins-base', 'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad', 'gstreamer1-plugins-ugly', 'gstreamer1-libav', 'gstreamer1-nice',
                'gstreamer1-rtsp-server']


class BuildRequest(build_utils.BuildRequest):
    def __init__(self, host, platform, arch_name, dir_path, prefix_path):
        build_utils.BuildRequest.__init__(self, platform, arch_name, dir_path, prefix_path)

        self.host = host

    def get_system_libs(self, with_nvidia, with_wpe, with_mongo, with_gstreamer, repo_build):
        platform = self.platform_
        platform_name = platform.name()
        ar = platform.architecture()
        dep_libs = []

        current_system = None
        if platform_name == 'linux':
            distribution = system_info.linux_get_dist()
            self.set_linux_hostname()
            if distribution == 'DEBIAN':
                current_system = Debian()
            elif distribution == 'RHEL':
                current_system = RedHat()
            elif distribution == 'ARCH':
                current_system = Arch()
        elif platform_name == 'freebsd':
            current_system = FreeBSD()
        elif platform_name == 'macosx':
            current_system = MacOSX()
        elif platform_name == 'windows':
            if ar.bit() == 64:
                current_system = Windows64()
            elif ar.bit() == 32:
                current_system = Windows32()

        if not current_system:
            raise NotImplementedError("Unknown platform '%s'" % platform_name)

        dep_libs.extend(current_system.get_required_exec())
        dep_libs.extend(current_system.get_build_exec())

        if with_gstreamer:
            dep_libs.extend(current_system.get_build_gst_exec())
            if repo_build:
                dep_libs.extend(current_system.get_gst_repo_libs())
            else:
                dep_libs.extend(current_system.get_gst_build_libs())

        if with_nvidia:
            dep_libs.extend(current_system.get_nvidia_libs())

        if with_wpe:
            dep_libs.extend(current_system.get_wpe_libs())

        if with_mongo:
            dep_libs.extend(current_system.get_mongo_libs())

        return dep_libs

    def set_linux_hostname(self):
        with open("/etc/hostname", "w+") as f:
            f.write(self.host)

    def prepare_docker(self):
        utils.regenerate_dbus_machine_id()

    def install_system(self, with_nvidia, with_wpe, with_mongo, with_gstreamer, repo_build):
        dep_libs = self.get_system_libs(with_nvidia=with_nvidia, with_wpe=with_wpe, with_mongo=with_mongo,
                                        with_gstreamer=with_gstreamer, repo_build=repo_build)
        for lib in dep_libs:
            self._install_package(lib)

        rust_home = self._install_rust_package()
        env_path = os.environ.get("PATH")
        os.environ["PATH"] = "{0}:{1}/bin".format(env_path, rust_home)
        platform = self.platform()
        platform_name = platform.name()

        # post install step
        if platform_name == 'linux':
            distribution = system_info.linux_get_dist()
            if distribution == 'RHEL':
                subprocess.call(['ln', '-sf', '/usr/bin/ninja-build', '/usr/bin/ninja'])
        elif platform_name == 'freebsd':
            subprocess.call(['dbus-uuidgen', '--ensure'])

    def install_tools(self):
        self.update_pyfastostream()
        self._install_via_pip3('speedtest-cli')

        args_cargo = ['--version', '0.9.21', 'cargo-c']
        self._install_via_cargo_list(args_cargo)

    def install_nginx(self):
        self._install_package('nginx')
        # post install step
        platform = self.platform()
        platform_name = platform.name()
        if platform_name == 'linux':
            src = os.path.join(_file_path, "nginx")
            dst = "/etc/nginx/sites-enabled"

            names = map(lambda name: (os.path.join(src, name), os.path.join(dst, name)), os.listdir(src))

            for srcname, dstname in names:
                shutil.copy2(srcname, dstname)


    def build_faac(self):
        compiler_flags = []
        self._download_and_build_via_bootstrap(FAAC_URL, compiler_flags)

    def build_libva(self):
        compiler_flags_va = ['--buildtype=release']
        compiler_flags_va_utils = ['--buildtype=release', '-Ddrm=true']
        self._clone_and_build_via_meson_system(LIBVA_URL, compiler_flags_va)
        self._clone_and_build_via_meson_system(LIBVA_UTILS_URL, compiler_flags_va_utils)

    def build_vaapi(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson_system(INTEL_VAAPI_DRIVER_URL, compiler_flags)

    def build_mfx(self):
        compiler_flags = []
        self._clone_and_build_via_cmake(GMM_LIB_URL, compiler_flags)
        self._clone_and_build_via_cmake(INTEL_MEDIA_DRIVER_URL, compiler_flags)
        self._clone_and_build_via_cmake(MEDIA_SDK_URL, ['-DENABLE_OPENCL=OFF'])

    def build_openh264(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(OPENH264_URL, compiler_flags, branch='v2.1.1')

    def build_wpe(self, version):
        compiler_flags = []
        url = '{0}/libwpe-{1}.{2}'.format(WPE_URL, version, WPE_ARCH_EXT)
        self._download_and_build_via_cmake(url, compiler_flags)

    def build_wpe_backend(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}/wpebackend-fdo-{1}.{2}'.format(WPE_BACKEND_URL, version, WPE_BACKEND_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])

    def build_wpe_webkit(self, version):
        compiler_flags = ['-DPORT=WPE', '-DUSE_SOUP2=ON', '-DENABLE_ACCESSIBILITY=OFF', '-DUSE_OPENJPEG=OFF',
                          '-DUSE_WOFF2=OFF', '-DUSE_LCMS=OFF', '-DUSE_AVIF=OFF', '-DENABLE_BUBBLEWRAP_SANDBOX=OFF', '-DENABLE_INTROSPECTION=OFF']
        url = '{0}/wpewebkit-{1}.{2}'.format(WPE_WEBKIT_URL, version, WPE_WEBKIT_ARCH_EXT)
        self._download_and_build_via_cmake(url, compiler_flags)

    def build_srt(self, version):
        compiler_flags = []
        url = '{0}/v{1}.{2}'.format(SRT_SRC_URL, version, SRT_ARCH_EXT)
        self._download_and_build_via_cmake(url, compiler_flags)

    def build_opencv(self):
        compiler_flags = ['-DBUILD_JAVA=OFF', '-DBUILD_TESTS=OFF', '-DWITH_GSTREAMER=OFF',
                          '-DOPENCV_GENERATE_PKGCONFIG=ON']
        self._clone_and_build_via_cmake(OPENCV_URL, compiler_flags)

    def build_libyaml(self):
        cmake_flags = []
        self._clone_and_build_via_cmake(build_utils.generate_fastogt_github_path('libyaml'), cmake_flags)

    def build_fastoml(self):
        cmake_flags = []
        self._clone_and_build_via_cmake(build_utils.generate_fastogt_github_path('fastoml'), cmake_flags)

    def build_aws(self):
        cmake_flags = ['-DBUILD_ONLY=s3;sts']
        self._clone_and_build_via_cmake(AWS_SDK_URL, cmake_flags)

    def build_ndi(self):
        cmake_flags = []
        self._clone_and_build_via_cmake(NDI_URL, cmake_flags)

    def build_gstreamer(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gstreamer/gstreamer-{1}.{2}'.format(GSTREAMER_SRC_ROOT, version, GSTREAMER_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])

    def build_gst_plugins_base(self, version):
        compiler_flags = ['--buildtype=release', '-Dexamples=disabled']
#
        url = '{0}gst-plugins-base/gst-plugins-base-{1}.{2}'.format(GST_PLUGINS_BASE_SRC_ROOT, version, GST_PLUGINS_BASE_ARCH_EXT)
        patch_files = [
            self.get_patch_file_path("gst-plugins-base.patch")
        ]

        self._download_and_build_via_meson(url, compiler_flags, patch_files)

    def get_patch_file_path(self, patch_file):
        return os.path.join(_file_path, "fastogt_patch", "{0}".format(patch_file))

    def build_gst_plugins_good(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gst-plugins-good/gst-plugins-good-{1}.{2}'.format(GST_PLUGINS_GOOD_SRC_ROOT, version,
                                                                    GST_PLUGINS_GOOD_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])

    def build_gst_plugins_bad(self, version, mfx: bool, vaapi: bool):
        compiler_flags = ['--buildtype=release', '-Dgpl=enabled']
        url = '{0}gst-plugins-bad/gst-plugins-bad-{1}.{2}'.format(GST_PLUGINS_BAD_SRC_ROOT, version,
                                                                  GST_PLUGINS_BAD_ARCH_EXT)
        patch_files = [
            self.get_patch_file_path("gst-plugins-bad.patch")
        ]

        self._download_and_build_via_meson(url, compiler_flags, patch_files)

        if mfx:
            compiler_flags_mfx = ['-DWITH_WAYLAND=OFF', '-DMFX_SINK=OFF']
            self._clone_and_build_via_cmake(GSTREAMER_MFX_URL, compiler_flags_mfx)
        if vaapi:
            compiler_flags_vaapi = ['--buildtype=release']
            url = '{0}gstreamer-vaapi/gstreamer-vaapi-{1}.{2}'.format(GSTREAMER_SRC_ROOT, version, GSTREAMER_ARCH_EXT)
            self._download_and_build_via_meson(url, compiler_flags_vaapi, [])

    def build_gst_plugins_ugly(self, version):
        compiler_flags = ['--buildtype=release', '-Dgpl=enabled']
        url = '{0}gst-plugins-ugly/gst-plugins-ugly-{1}.{2}'.format(GST_PLUGINS_UGLY_SRC_ROOT, version,
                                                                    GST_PLUGINS_UGLY_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])

    def build_gst_fastoml(self):
        compiler_flags = ['--buildtype=release']
        url = build_utils.generate_fastogt_github_path('gst-fastoml')
        self._clone_and_build_via_meson(url, compiler_flags)

    def build_gst_awss3(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(AWS_S3_URL, compiler_flags)

    def build_gst_rs_plugins(self):
        self._install_package('curl')
        plugins = ["gst-plugin-ndi", "gst-plugin-webrtchttp"]
        self._clone_and_build_via_cargo_c_arr(GST_RUST_PLUGINS, plugins)

    def build_gst_libav(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gst-libav/gst-libav-{1}.{2}'.format(GST_LIBAV_SRC_ROOT, version, GST_LIBAV_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])

    def build_gst_nice(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(GST_NICE_URL, compiler_flags)

    def build_gst_rtsp(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gst-rtsp-server/gst-rtsp-server-{1}.{2}'.format(GST_RTSP_SRC_ROOT, version, GST_RTSP_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags, [])


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    meson_default_version = '0.62.0'
    srt_default_version = '1.5.3'
    gstreamer_default_version = '1.22.10'
    # https://wpewebkit.org/release/
    wpe_version = '1.14.1'
    wpe_backend_version = '1.14.2'
    wpe_webkit_version = '2.42.0'

    host_os = system_info.get_os()
    arch_host_os = system_info.get_arch_name()

    parser = argparse.ArgumentParser(prog='build_env', usage='%(prog)s [options]')
    # system
    system_grp = parser.add_mutually_exclusive_group()
    system_grp.add_argument('--with-system', help='build with system dependencies (default)', dest='with_system',
                            action='store_true', default=True)
    system_grp.add_argument('--without-system', help='build without system dependencies', dest='with_system',
                            action='store_false', default=False)

    # tools
    tools_grp = parser.add_mutually_exclusive_group()
    tools_grp.add_argument('--with-tools', help='build with tools dependencies (default)', dest='with_tools',
                           action='store_true', default=True)
    tools_grp.add_argument('--without-tools', help='build without tools dependencies', dest='with_tools',
                           action='store_false', default=False)

    # nginx
    nginx_grp = parser.add_mutually_exclusive_group()
    nginx_grp.add_argument('--with-nginx', help='install nginx and fastocloud scripts', dest='with_nginx',
                           action='store_true', default=True)
    nginx_grp.add_argument('--without-nginx', help='without nginx and fastocloud scripts', dest='with_nginx',
                           action='store_false',
                           default=False)

    # faac
    faac_grp = parser.add_mutually_exclusive_group()
    faac_grp.add_argument('--with-faac', help='build faac (default, version: git master)', dest='with_faac',
                          action='store_true', default=True)
    faac_grp.add_argument('--without-faac', help='build without faac', dest='with_faac', action='store_false',
                          default=False)

    # voaac
    voaac_grp = parser.add_mutually_exclusive_group()
    voaac_grp.add_argument('--with-voaac', help='build voaac (default, version: git master)', dest='with_voaac',
                           action='store_true', default=True)
    voaac_grp.add_argument('--without-voaac', help='build without voaac', dest='with_voaac', action='store_false',
                           default=False)

    # meson
    meson_grp = parser.add_mutually_exclusive_group()
    meson_grp.add_argument('--with-meson', help='build meson (default, version:{0})'.format(meson_default_version),
                           dest='with_meson', action='store_true', default=True)
    meson_grp.add_argument('--without-meson', help='build without meson', dest='with_meson', action='store_false',
                           default=False)
    parser.add_argument('--meson-version', help='meson version (default: {0})'.format(meson_default_version),
                        default=meson_default_version)

    # openh264
    openh264_grp = parser.add_mutually_exclusive_group()
    openh264_grp.add_argument('--with-openh264', help='build openh264 (default, version: git master)',
                              dest='with_openh264',
                              action='store_true', default=True)
    openh264_grp.add_argument('--without-openh264', help='build without openh264', dest='with_openh264',
                              action='store_false',
                              default=False)

    # libva
    libva_grp = parser.add_mutually_exclusive_group()
    libva_grp.add_argument('--with-libva', help='build libva (default, version: git master)',
                           dest='with_libva',
                           action='store_true', default=False)
    libva_grp.add_argument('--without-libva', help='build without libva', dest='with_libva',
                           action='store_false',
                           default=True)

    # vaapi
    vaapi_grp = parser.add_mutually_exclusive_group()
    vaapi_grp.add_argument('--with-vaapi', help='build vaapi (default, version: git master)',
                           dest='with_vaapi',
                           action='store_true', default=False)
    vaapi_grp.add_argument('--without-vaapi', help='build without vaapi', dest='with_vaapi',
                           action='store_false',
                           default=True)

    # mfx
    mfx_grp = parser.add_mutually_exclusive_group()
    mfx_grp.add_argument('--with-mfx', help='build mfx (default, version: git master)',
                         dest='with_mfx',
                         action='store_true', default=False)
    mfx_grp.add_argument('--without-mfx', help='build without mfx', dest='with_mfx',
                         action='store_false',
                         default=True)

    # nvidia
    nvidia_grp = parser.add_mutually_exclusive_group()
    nvidia_grp.add_argument('--with-nvidia', help='build nvidia (default, version: git master)', dest='with_nvidia',
                            action='store_true', default=False)
    nvidia_grp.add_argument('--without-nvidia', help='build without nvidia', dest='with_nvidia', action='store_false',
                            default=True)

    # wpe
    wpe_grp = parser.add_mutually_exclusive_group()
    wpe_grp.add_argument('--with-wpe', help='build wpe (default, version: git master)', dest='with_wpe',
                         action='store_true', default=False)
    wpe_grp.add_argument('--without-wpe', help='build without wpe', dest='with_wpe', action='store_false', default=True)

    # mongo
    mongo_grp = parser.add_mutually_exclusive_group()
    mongo_grp.add_argument('--with-mongo', help='build mongo (default, version: git master)',
                           dest='with_mongo',
                           action='store_true', default=False)
    mongo_grp.add_argument('--without-mongo', help='build without mongo', dest='with_mongo',
                           action='store_false',
                           default=True)

    # srt
    srt_grp = parser.add_mutually_exclusive_group()
    srt_grp.add_argument('--with-srt', help='build srt (default, version:{0})'.format(srt_default_version),
                         dest='with_srt', action='store_true', default=True)
    srt_grp.add_argument('--without-srt', help='build without srt', dest='with_srt', action='store_false',
                         default=False)
    parser.add_argument('--srt-version', help='srt version (default: {0})'.format(srt_default_version),
                        default=srt_default_version)

    # ffmpeg
    ffmpeg_grp = parser.add_mutually_exclusive_group()
    ffmpeg_grp.add_argument('--with-ffmpeg', help='build ffmpeg (default, version: git master)', dest='with_ffmpeg',
                            action='store_true', default=True)
    ffmpeg_grp.add_argument('--without-ffmpeg', help='build without ffmpeg', dest='with_ffmpeg', action='store_false',
                            default=False)

    # opencv
    opencv_grp = parser.add_mutually_exclusive_group()
    opencv_grp.add_argument('--with-opencv', help='build opencv (default, version: git master)',
                            dest='with_opencv',
                            action='store_true', default=False)
    opencv_grp.add_argument('--without-opencv', help='build without opencv', dest='with_opencv',
                            action='store_false',
                            default=True)

    # json-c
    jsonc_grp = parser.add_mutually_exclusive_group()
    jsonc_grp.add_argument('--with-json-c', help='build json-c (default, version: git master)', dest='with_jsonc',
                           action='store_true', default=True)
    jsonc_grp.add_argument('--without-json-c', help='build without json-c', dest='with_jsonc', action='store_false',
                           default=False)

    # libev
    libev_grp = parser.add_mutually_exclusive_group()
    libev_grp.add_argument('--with-libev', help='build libev (default, version: git master)', dest='with_libev',
                           action='store_true', default=True)
    libev_grp.add_argument('--without-libev', help='build without libev', dest='with_libev', action='store_false',
                           default=False)

    # common
    common_grp = parser.add_mutually_exclusive_group()
    common_grp.add_argument('--with-common', help='build common (default, version: git master)', dest='with_common',
                            action='store_true', default=True)
    common_grp.add_argument('--without-common', help='build without common', dest='with_common',
                            action='store_false',
                            default=False)

    # fastotv_cpp
    fastotv_cpp_grp = parser.add_mutually_exclusive_group()
    fastotv_cpp_grp.add_argument('--with-fastotv-cpp', help='build fastotv_cpp (default, version: git master)',
                                 dest='with_fastotv_cpp', action='store_true', default=True)
    fastotv_cpp_grp.add_argument('--without-fastotv-cpp', help='build without fastotv_cpp', dest='with_fastotv_cpp',
                                 action='store_false', default=False)

    # libyaml
    libyaml_grp = parser.add_mutually_exclusive_group()
    libyaml_grp.add_argument('--with-libyaml-cpp', help='build libyaml (default, version: git master)',
                                 dest='with_libyaml', action='store_true', default=True)
    libyaml_grp.add_argument('--without-libyaml-cpp', help='build without libyaml', dest='with_libyaml',
                                 action='store_false', default=False)

    # fastoml
    fastoml_grp = parser.add_mutually_exclusive_group()
    fastoml_grp.add_argument('--with-fastoml', help='build fastoml (default, version: git master)',
                             dest='with_fastoml',
                             action='store_true', default=False)
    fastoml_grp.add_argument('--without-fastoml', help='build without fastoml', dest='with_fastoml',
                             action='store_false',
                             default=True)

    # aws
    aws_grp = parser.add_mutually_exclusive_group()
    aws_grp.add_argument('--with-aws', help='build aws (default, version: git master)',
                         dest='with_aws',
                         action='store_true', default=False)
    aws_grp.add_argument('--without-aws', help='build without aws', dest='with_aws',
                         action='store_false',
                         default=True)

    # ndi 
    ndi_grp = parser.add_mutually_exclusive_group()
    ndi_grp.add_argument('--with-ndi', help='build ndi',
                         dest='with_ndi',
                         action='store_true', default=False)
    ndi_grp.add_argument('--without-ndi', help='build without ndi', dest='with_ndi',
                         action='store_false',
                         default=True)

    # gstreamer
    gstreamer_grp = parser.add_mutually_exclusive_group()
    gstreamer_grp.add_argument('--with-gstreamer',
                               help='build gstreamer (default, version:{0})'.format(gstreamer_default_version),
                               dest='with_gstreamer', action='store_true', default=True)
    gstreamer_grp.add_argument('--without-gstreamer', help='build without gstreamer', dest='with_gstreamer',
                               action='store_false',
                               default=False)
    parser.add_argument('--gstreamer-version',
                        help='gstreamer version (default: {0})'.format(gstreamer_default_version),
                        default=gstreamer_default_version)

    # gst-plugins-base
    gst_plugins_base_grp = parser.add_mutually_exclusive_group()
    gst_plugins_base_grp.add_argument('--with-gst-plugins-base',
                                      help='build gst-plugins-base (default, version:{0})'.format(
                                          gstreamer_default_version),
                                      dest='with_gst_plugins_base', action='store_true', default=True)
    gst_plugins_base_grp.add_argument('--without-gst-plugins-base', help='build without gst-plugins-base',
                                      dest='with_gst_plugins_base',
                                      action='store_false',
                                      default=False)

    # gst-plugins-good
    gst_plugins_good_grp = parser.add_mutually_exclusive_group()
    gst_plugins_good_grp.add_argument('--with-gst-plugins-good',
                                      help='build gst-plugins-good (default, version:{0})'.format(
                                          gstreamer_default_version),
                                      dest='with_gst_plugins_good', action='store_true', default=True)
    gst_plugins_good_grp.add_argument('--without-gst-plugins-good', help='build without gst-plugins-good',
                                      dest='with_gst_plugins_good',
                                      action='store_false',
                                      default=False)

    # gst-plugins-bad
    gst_plugins_bad_grp = parser.add_mutually_exclusive_group()
    gst_plugins_bad_grp.add_argument('--with-gst-plugins-bad',
                                     help='build gst-plugins-bad (default, version:{0})'.format(
                                         gstreamer_default_version),
                                     dest='with_gst_plugins_bad', action='store_true', default=True)
    gst_plugins_bad_grp.add_argument('--without-gst-plugins-bad', help='build without gst-plugins-bad',
                                     dest='with_gst_plugins_bad',
                                     action='store_false',
                                     default=False)

    # gst-plugins-ugly
    gst_plugins_ugly_grp = parser.add_mutually_exclusive_group()
    gst_plugins_ugly_grp.add_argument('--with-gst-plugins-ugly',
                                      help='build gst-plugins-ugly (default, version:{0})'.format(
                                          gstreamer_default_version),
                                      dest='with_gst_plugins_ugly', action='store_true', default=True)
    gst_plugins_ugly_grp.add_argument('--without-gst-plugins-ugly', help='build without gst-plugins-ugly',
                                      dest='with_gst_plugins_ugly',
                                      action='store_false',
                                      default=False)

    # gst-plugins-rs
    gst_plugins_rs_grp = parser.add_mutually_exclusive_group()
    gst_plugins_rs_grp.add_argument('--with-gst-rs-plugins', help='build with rust gst-plugins', dest='with_gst_rs_plugins', action='store_true', default=False)
    gst_plugins_rs_grp.add_argument('--without-gst-rs-plugins', help='build without gst-plugins-rs', dest='with_gst_rs_plugins', action='store_false', default=True)

    # gst-fastoml
    gst_fastoml_grp = parser.add_mutually_exclusive_group()
    gst_fastoml_grp.add_argument('--with-gst-fastoml', help='build gst-fastoml (default, version: git master)',
                                 dest='with_gst_fastoml',
                                 action='store_true', default=False)
    gst_fastoml_grp.add_argument('--without-gst-fastoml', help='build without gst-fastoml', dest='with_gst_fastoml',
                                 action='store_false',
                                 default=True)

    # gst-aws-s3
    gst_awss3_grp = parser.add_mutually_exclusive_group()
    gst_awss3_grp.add_argument('--with-gst-awss3', help='build gst-awss3 (default, version: git master)',
                               dest='with_gst_awss3',
                               action='store_true', default=False)
    gst_awss3_grp.add_argument('--without-gst-awss3', help='build without gst-awss3', dest='with_gst_awss3',
                               action='store_false',
                               default=True)

    # gst-libav
    gst_libav_grp = parser.add_mutually_exclusive_group()
    gst_libav_grp.add_argument('--with-gst-libav',
                               help='build gst-libav (default, version:{0})'.format(
                                   gstreamer_default_version),
                               dest='with_gst_libav', action='store_true', default=True)
    gst_libav_grp.add_argument('--without-gst-libav', help='build without gst-libav',
                               dest='with_gst_libav',
                               action='store_false',
                               default=False)

    # gst-nice
    gst_nice_grp = parser.add_mutually_exclusive_group()
    gst_nice_grp.add_argument('--with-gst-nice',
                              help='build gst-nice (default, version: git master)',
                              dest='with_gst_nice', action='store_true', default=True)
    gst_nice_grp.add_argument('--without-gst-nice', help='build without gst-nice',
                              dest='with_gst_nice',
                              action='store_false',
                              default=False)

    # gst-rtsp-server
    gst_rtsp_grp = parser.add_mutually_exclusive_group()
    gst_rtsp_grp.add_argument('--with-gst-rtsp',
                              help='build gst-rtsp (default, version:{0})'.format(
                                  gstreamer_default_version),
                              dest='with_gst_rtsp', action='store_true', default=True)
    gst_rtsp_grp.add_argument('--without-gst-rtsp', help='build without gst-rtsp',
                              dest='with_gst_rtsp',
                              action='store_false',
                              default=False)

    # other
    parser.add_argument("--hostname", help="server hostname (default: {0})".format(DEFAULT_HOSTNAME), default=DEFAULT_HOSTNAME)
    parser.add_argument('--platform', help='build for platform (default: {0})'.format(host_os), default=host_os)
    parser.add_argument('--architecture', help='architecture (default: {0})'.format(arch_host_os),
                        default=arch_host_os)
    parser.add_argument('--prefix', help='prefix path (default: None)', default=None)
    parser.add_argument('--docker', help='docker build (default: False)', dest='docker', action='store_true',
                        default=False)

    parser.add_argument('--install-other-packages',
                        help='install other packages (--with-system, --with-tools --with-meson --with-jsonc --with-libev) (default: True)',
                        dest='install_other_packages', type=str2bool, default=True)
    parser.add_argument('--install-fastogt-packages',
                        help='install FastoGT packages (--with-common --with-fastotv-cpp --with-libyaml) (default: True)',
                        dest='install_fastogt_packages', type=str2bool, default=True)
    parser.add_argument('--install-gstreamer-packages',
                        help='install GStreamer packages  (--with-gstreamer --with-gst-plugins-base --with-gst-plugins-good --with-gst-plugins-bad --with-gst-plugins-ugly --with-gst-libav --with-gst-rtsp) (default: True)',
                        dest='install_gstreamer_packages', type=str2bool, default=True)

    argv = parser.parse_args()

    arg_hostname = argv.hostname
    arg_platform = argv.platform
    arg_prefix_path = argv.prefix
    argv_docker = argv.docker
    arg_architecture = argv.architecture
    arg_install_other_packages = argv.install_other_packages
    arg_install_fastogt_packages = argv.install_fastogt_packages
    arg_install_gstreamer_packages = argv.install_gstreamer_packages

    request = BuildRequest(arg_hostname, arg_platform, arg_architecture, 'build_' + arg_platform + '_env', arg_prefix_path)
    if argv_docker:
        request.prepare_docker()

    if argv.with_system and arg_install_other_packages:
        request.install_system(with_nvidia=argv.with_nvidia, with_wpe=argv.with_wpe, with_mongo=argv.with_mongo,
                               with_gstreamer=True, repo_build=False)

    if argv.with_tools and arg_install_other_packages:
        request.install_tools()

    if argv.with_nginx and arg_install_other_packages:
        request.install_nginx()

    if argv.with_faac and arg_install_other_packages:
        request.build_faac()

    if argv.with_meson and arg_install_other_packages:
        request.build_meson(argv.meson_version)

    if argv.with_openh264 and arg_install_other_packages:
        request.build_openh264()

    if (argv.with_libva or argv.with_mfx) and arg_install_other_packages:
        request.build_libva()

    build_vaapi = argv.with_vaapi and arg_install_other_packages
    if build_vaapi:
        request.build_vaapi()

    build_mfx = argv.with_mfx and arg_install_other_packages
    if build_mfx:
        request.build_mfx()

    build_wpe = argv.with_wpe and arg_install_other_packages
    if build_wpe:
        request.build_wpe(wpe_version)
        request.build_wpe_backend(wpe_backend_version)

    if argv.with_srt and arg_install_other_packages:
        request.build_srt(argv.srt_version)

    if argv.with_ffmpeg and arg_install_other_packages:
        request.build_ffmpeg()

    if argv.with_opencv and arg_install_other_packages:
        request.build_opencv()

    if argv.with_jsonc and arg_install_other_packages:
        request.build_jsonc()
    if argv.with_libev and arg_install_other_packages:
        request.build_libev()
    if argv.with_aws and arg_install_other_packages:
        request.build_aws()
    if argv.with_common and arg_install_fastogt_packages:
        request.build_common()

    if argv.with_ndi and arg_install_other_packages:
        request.build_ndi()

    if argv.with_fastotv_cpp and arg_install_fastogt_packages:
        request.build_fastotv_cpp()

    if argv.with_libyaml and arg_install_fastogt_packages:
        request.build_libyaml()

    if argv.with_fastoml and arg_install_fastogt_packages:
        request.build_fastoml()

    if argv.with_gstreamer and arg_install_gstreamer_packages:
        request.build_gstreamer(argv.gstreamer_version)

    if argv.with_gst_plugins_base and arg_install_gstreamer_packages:
        request.build_gst_plugins_base(argv.gstreamer_version)

    if build_wpe:
        request.build_wpe_webkit(wpe_webkit_version)

    if argv.with_gst_plugins_good and arg_install_gstreamer_packages:
        request.build_gst_plugins_good(argv.gstreamer_version)

    if argv.with_gst_nice and arg_install_gstreamer_packages:
        request.build_gst_nice()

    if argv.with_gst_plugins_bad and arg_install_gstreamer_packages:
        request.build_gst_plugins_bad(argv.gstreamer_version, build_mfx, build_vaapi)

    if argv.with_gst_plugins_ugly and arg_install_gstreamer_packages:
        request.build_gst_plugins_ugly(argv.gstreamer_version)

    if argv.with_gst_fastoml and arg_install_gstreamer_packages:
        request.build_gst_fastoml()

    if argv.with_gst_awss3 and arg_install_gstreamer_packages:
        request.build_gst_awss3()

    if argv.with_gst_rs_plugins and arg_install_gstreamer_packages:
        request.build_gst_rs_plugins()

    if argv.with_gst_libav and arg_install_gstreamer_packages:
        request.build_gst_libav(argv.gstreamer_version)

    if argv.with_gst_rtsp and arg_install_gstreamer_packages:
        request.build_gst_rtsp(argv.gstreamer_version)

    check_plugins()
