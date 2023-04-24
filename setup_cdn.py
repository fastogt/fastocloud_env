#!/usr/bin/env python3

import os
import sys
import subprocess

if sys.version_info < (3, 4):
    print(
        "Tried to start script with an unsupported version of Python. setup_cdn requires Python 3.5 or greater"
    )
    sys.exit(1)

try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip3", "install", "pyyaml"])

import socket

from functools import partial, reduce
from argparse import ArgumentParser
from contextlib import closing

from typing import Dict, List


NGINX_TEMPLATE = """
server {{
    access_log {access_log};
    error_log {error_log};

    {listen_port} 

    server_name _;

    location = /status {{
        stub_status;
    }}

    location / {{
        # Disable cache
        add_header Cache-Control no-cache;

        # CORS setup
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length';
        # allow CORS preflight requests
        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }}

        types {{
            application/vnd.apple.mpegurl m3u8;
            video/mp2t ts;
        }}

        alias {alias};
    }}
}}
"""

# TODO
FASTOCLOUD_CONFIG_TEMPLATE = """
log_path: ~/fastocloud_pro.log
log_level: DEBUG
host: 127.0.0.1:6317
alias: {alias} 
hls_host: https://0.0.0.0:8000
vods_host: https://0.0.0.0:7000
cods_host: http://0.0.0.0:6000

hls_dir: ~/streamer/hls
vods_dir: ~/streamer/vods
cods_dir: ~/streamer/cods
timeshifts_dir: ~/streamer/timeshifts
feedback_dir: ~/streamer/feedback
proxy_dir: ~/streamer/proxy
data_dir: ~/streamer/data

cods_ttl: 60
pyfastostream_path: /usr/local/bin/pyfastostream
files_ttl: 8640000
report_node_stats: 10

{nodes}

#https:
#    key: /etc/letsencrypt/live/fastocloud.com-0001/privkey.pem
#    cert: /etc/letsencrypt/live/fastocloud.com-0001/fullchain.pem
"""

HLS_TEMPLATE = {
    "name": "hls_nodes",
    "filename": "fastocloud_hls",
    "access_log": "/var/log/nginx/fastocloud_hls_{port}_access.log",
    "error_log": "/var/log/nginx/fastocloud_hls_{port}_error.log",
    "alias": "/home/fastocloud/streamer/hls/",
}

VODS_TEMPLATE = {
    "name": "vods_nodes",
    "filename": "fastocloud_vods",
    "access_log": "/var/log/nginx/fastocloud_vods_{port}_access.log",
    "error_log": "/var/log/nginx/fastocloud_vods_{port}_error.log",
    "alias": "/home/fastocloud/streamer/vods/",
}

CODS_TEMPLATE = {
    "name": "cods_nodes",
    "filename": "fastocloud_cods",
    "access_log": "/var/log/nginx/fastocloud_cods_{port}_access.log",
    "error_log": "/var/log/nginx/fastocloud_cods_{port}_error.log",
    "alias": "/home/fastocloud/streamer/cods/",
}


# TODO
FASTOCLOUD_PRO_TEMPLATE = {
    "filename": "fastocloud_pro.conf",
}

# TODO
FASTOCLOUD_PRO_ML_TEMPLATE = {
    "filename": "fastocloud_pro_ml.conf",
}


FASTOCLOUD_CONFIG_DIR = "/etc"

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

        self.__already_used_ports: List[int] = []


    def run(self) -> None:
        argv = self._parser.parse_args()

        alias = argv.alias
        connections = argv.connections
        ml_version = argv.ml_version

        self._is_open_port = partial(is_open_socket, "127.0.0.1")

        print("Start building NGINX configs for HLS, VODS, CODS...")
        ports = self._build_nginx_configs(connections)
        print("Successfullly build NGINX configs")

        print("Start building Fastocloud config...")
        self._build_fastocloud_config(alias, ports, ml_version)
        print("Successfullly build Fastocloud config")

    # TODO
    def _build_fastocloud_config(
        self, alias: str, ports: Dict[str, List[int]], ml_version: bool
    ) -> None:
        template = FASTOCLOUD_PRO_ML_TEMPLATE if ml_version else FASTOCLOUD_PRO_TEMPLATE

        def config_template(port: int) -> Dict[str, str]:
            return {"host": f"http://0.0.0.0:{port}", "type": 1}

        for k, v in ports.items():
            ports[k] = list(map(lambda port: config_template(port), v))

        nodes = str(yaml.dump(ports))

        new_config = FASTOCLOUD_CONFIG_TEMPLATE.format(alias=alias, nodes=nodes)

        return self._write_fastocloud_config(template["filename"], new_config)


    def _write_fastocloud_config(self, filename: str, config: str) -> None:
        config_path = os.path.join(FASTOCLOUD_CONFIG_DIR, filename)

        with open(config_path, "w+") as f:
            f.write(config)

    def _build_nginx_configs(self, connections: int) -> Dict[str, List[int]]:
        def closure(
            acc: Dict[str, List[int]], template: Dict[str, str]
        ) -> Dict[str, List[int]]:
            listen_ports = self.__get_listen_ports(connections)

            new_config = ""

            for port in listen_ports:
                port_string = self.__get_listen_port_string(port)

                server = NGINX_TEMPLATE.format(
                    access_log=template["access_log"].format(port=port),
                    error_log=template["error_log"].format(port=port),
                    listen_port=port_string,
                    alias=template["alias"],
                ).expandtabs(4)

                new_config += "\n" + server

            self._write_nginx_config(template["filename"], new_config)

            acc[template["name"]] = listen_ports

            return acc

        return reduce(
            lambda acc, template: closure(acc, template),
            (HLS_TEMPLATE, VODS_TEMPLATE, CODS_TEMPLATE),
            {},
        )

    def _write_nginx_config(self, filename: str, config: str) -> None:
        available_path = os.path.join(NGINX_SITES_AVAILABLE_FOLDER, filename)
        enabled_path = os.path.join(NGINX_SITES_ENABLED_FOLDER, filename)

        with open(available_path, "w+") as available, open(
            enabled_path, "w+"
        ) as enabled:
            enabled.write(config)
            available.write(config)

    def __get_listen_ports(self, connections: int) -> List[int]:
        disabled_ports_gen = filter(
            None,
            map(
                lambda port: port
                if not self._is_open_port(port) and port not in self.__already_used_ports
                else None,
                range(65536),
            ),
        )
        first_connections_disabled_ports = list(
            map(lambda _: next(disabled_ports_gen), range(connections))
        )
        self.__already_used_ports.extend(first_connections_disabled_ports)
        return first_connections_disabled_ports

    def __get_listen_port_string(self, port: int) -> str:
        return f"listen {port};\n\tlisten[::]:{port};\n"

    def __init_parser(self) -> ArgumentParser:
        parser = ArgumentParser(prog=self._prog, usage=self._usage)

        parser.add_argument("--alias", help="nodes hostname alias", default="localhost")
        parser.add_argument(
            "--connections", help="number of ports to open", type=int, default=100
        )
        parser.add_argument(
            "--ml-version",
            help="build for fastocloud ml version",
            action="store_true",
            default=False,
        )

        return parser


if __name__ == "__main__":
    app = CdnConfigCli("build_cdn", "%(prog)s [options]")
    app.run()
