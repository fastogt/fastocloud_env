#!/usr/bin/env python3
import sys

# Check Python version before any external imports
if sys.version_info < (3, 10):
    print('Tried to start script with an unsupported version of Python. build_fastocloud_env_from_repo requires Python 3.10 or greater')
    sys.exit(1)

import argparse

from pyfastogt import system_info

from build_env import BuildRequest, str2bool, DEFAULT_HOSTNAME
from check_plugins import check_plugins


# Script for building environment on clean machine from repo


class BuildRequestRepo(BuildRequest):
    def __init__(self, host, platform, arch_name, dir_path, prefix_path):
        super(BuildRequestRepo, self).__init__(
            host, platform, arch_name, dir_path, prefix_path)


if __name__ == "__main__":
    host_os = system_info.get_os()
    arch_host_os = system_info.get_arch_name()

    parser = argparse.ArgumentParser(
        prog='build_env', usage='%(prog)s [options]')
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

    # other
    parser.add_argument("--hostname", help="server hostname (default: {0})".format(
        DEFAULT_HOSTNAME), default=DEFAULT_HOSTNAME)
    parser.add_argument(
        '--platform', help='build for platform (default: {0})'.format(host_os), default=host_os)
    parser.add_argument('--architecture', help='architecture (default: {0})'.format(arch_host_os),
                        default=arch_host_os)
    parser.add_argument(
        '--prefix', help='prefix path (default: None)', default=None)

    parser.add_argument('--install-other-packages',
                        help='install other packages (--with-system, --with-tools --with-meson --with-jsonc --with-libev) (default: True)',
                        dest='install_other_packages', type=str2bool, default=True)
    parser.add_argument('--install-fastogt-packages',
                        help='install FastoGT packages (--with-common --with-fastotv-cpp --with-libyaml) (default: True)',
                        dest='install_fastogt_packages', type=str2bool, default=True)

    argv = parser.parse_args()

    arg_hostname = argv.hostname
    arg_platform = argv.platform
    arg_prefix_path = argv.prefix
    arg_architecture = argv.architecture
    arg_install_other_packages = argv.install_other_packages
    arg_install_fastogt_packages = argv.install_fastogt_packages

    request = BuildRequestRepo(arg_hostname, arg_platform, arg_architecture,
                               'build_' + arg_platform + '_env', arg_prefix_path)
    if argv.with_system and arg_install_other_packages:
        request.install_system(with_nvidia=False, with_wpe=False, with_gstreamer=True,
                               repo_build=True)

    if argv.with_tools and arg_install_other_packages:
        request.install_tools()

    if argv.with_nginx and arg_install_other_packages:
        request.install_nginx()

    if argv.with_jsonc and arg_install_other_packages:
        request.build_jsonc()
    if argv.with_libev and arg_install_other_packages:
        request.build_libev()
    if argv.with_common and arg_install_fastogt_packages:
        request.build_common()

    if argv.with_fastotv_cpp and arg_install_fastogt_packages:
        request.build_fastotv_cpp()

    if argv.with_libyaml and arg_install_fastogt_packages:
        request.build_libyaml()

    check_plugins()
