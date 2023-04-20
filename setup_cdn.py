import os
import sys
import socket
import logging
import subprocess

from string import Template
from functools import partial, reduce
from argparse import ArgumentParser
from contextlib import closing

from typing import Dict, List

_file_path = os.path.dirname(os.path.abspath(__file__))

HLS_TEMPLATE = {
    "name": "hls",
    "filename": "fastocloud_hls_84",
    "path": os.path.join(_file_path, "nginx", "in", "fastocloud_hls_82.in")
}

VODS_TEMPLATE = {
    "name": "vods",
    "filename": "fastocloud_vods_84",
    "path": os.path.join(_file_path, "nginx", "in", "fastocloud_vods_83.in")
}

CODS_TEMPLATE = {
    "name": "cods",
    "filename": "fastocloud_cods_84",
    "path": os.path.join(_file_path, "nginx", "in", "fastocloud_cods_84.in")
}


FASTOCLOUD_PRO_TEMPLATE = {
    "filename": "fastocloud_pro.conf",
    "path": os.path.join(_file_path, "nginx", "in", "fastocloud_pro.in")
}

FASTOCLOUD_PRO_ML_TEMPLATE = {
    "filename": "fastocloud_pro_ml.conf",
    "path": os.path.join(_file_path, "nginx", "in", "fastocloud_pro_ml.in")
}


FASTOCLOUD_PRO_CONFIG_PATH = "/etc/fastocloud_pro.conf"
FASTOCLOUD_PRO_ML_CONFIG_PATH = "/etc/fastocloud_pro_ml.conf"

NGINX_SITES_AVAILABLE_FOLDER = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED_FOLDER = "/etc/nginx/sites-enabled"


def is_open_socket(host, port) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False


class CdnConfigCli:
    def __init__(self, prog: str, usage: str) -> None:
        self._prog = prog
        self._usage = usage

        self._parser = self.__init_parser()

    def run(self) -> None:
        argv = self._parser.parse_args()

        host = argv.host
        alias = argv.alias
        connections = argv.connections
        ml_version = argv.ml_version

        self._is_open_port = partial(is_open_socket, host)

        ports = self._build_nginx_configs(connections)
        self._build_fastocloud_config(host, alias, ports, ml_version)


    # TODO
    def _build_fastocloud_config(self, host: str, alias: str, ml_version: bool) -> None:
        template = FASTOCLOUD_PRO_ML_TEMPLATE if ml_version else FASTOCLOUD_PRO_TEMPLATE
        with open(template["path"], "r") as f:
            new_config = Template(f.read()).substitute()

    def _build_nginx_configs(self, connections: int) -> Dict[str, List[int]]:
        def closure(acc: Dict[str, List[int]], template: Dict[str, str]) -> List[int]:
            with open(template["path"], "r") as f:
                listen_ports = self.__get_listen_ports(connections)
                listen_ports_string = self.__get_listen_ports_string(listen_ports)

                new_config = Template(f.read()).substitute(listen_ports=listen_ports_string)
                self._write_nginx_config(template["filename"], new_config)

                acc[template["name"]] = listen_ports

        # for template in (HLS_TEMPLATE, VODS_TEMPLATE, CODS_TEMPLATE):
        #     with open(template["path"], "r") as f:
        #         listen_ports = self.__get_listen_ports(connections)

        #         listen_ports_string = self.__get_listen_ports_string(listen_ports)
        #         new_config = Template(f.read()).substitute(listen_ports=listen_ports_string)
        #         self._write_nginx_config(template["filename"], new_config)

        return reduce(lambda acc, template: closure(acc, template), (HLS_TEMPLATE, VODS_TEMPLATE, CODS_TEMPLATE), {})


    def _write_nginx_config(self, name: str, config: str) -> None:
        available_path = os.path.join(NGINX_SITES_AVAILABLE_FOLDER, name)
        enabled_path = os.path.join(NGINX_SITES_ENABLED_FOLDER, name)

        with open(available_path, "wx") as available, open(enabled_path, "wx") as enabled:
            enabled.write(config)
            available.write(config)

    def __get_listen_ports(self, connections: int) -> List[int]:
        disabled_ports_gen = filter(None, map(lambda port: port if not self._is_open_port(port) else None, range(65536)))
        return list(map(lambda _: next(disabled_ports_gen), range(connections)))
        

    def __get_listen_ports_string(self, connections: int) -> str:
        result, port = "", 0

        for _ in range(connections):
            if not self._is_open_port(port):
                result += f"listen {port};\nlisten[::]:{port};\n"

        return result

    def __init_parser(self) -> ArgumentParser:
        parser = ArgumentParser(prog=self._prog, usage=self._usage) 

        parser.add_argument("--host", help="nodes hostname", default="127.0.0.1")
        parser.add_argument("--alias", help="nodes hostname alias", default="localhost")
        parser.add_argument("--connections", help="number of ports to open", type=int, default=100)
        parser.add_argument("--ml-version", help="build for fastocloud ml version", action="store_true", default=False)

        return parser


if __name__ == "__main__":
    app = CdnConfigCli()
    app.run()
        



