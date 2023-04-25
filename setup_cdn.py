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
    __import__("yaml")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])

import yaml

import socket
import random

from functools import partial, reduce
from urllib import parse
from collections import defaultdict
from contextlib import closing

from typing import Dict, List, Any


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
host: {host} 
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
            return False
        else:
            return True


class CdnConfigBuilder:
    def __init__(self) -> None:
        self.__already_used_ports: List[int] = []

    def run(self) -> None:
        host = input("Host: ") or "127.0.0.1:6317"
        alias = input("Alias: ") or "fastocloud.com"

        silence = True if input("Silence [Y/n]") != "n" else False
        ml_version = True if input("ML version [Y/n]: ") != "n" else False

        print()

        self._is_open_port = partial(is_open_socket, "0.0.0.0")

        def get_user_input(
            acc: Dict[str, List[Dict[str, Any]]], template: Dict[str, str]
        ) -> Dict[str, List[Dict[str, Any]]]:
            print("Processing ", template["name"])

            while True:
                try:
                    connections = int(input("Number of nodes: "))
                except Exception:
                    continue

                break
            
            for _ in range(connections):
                while True:
                    try:
                        url_raw = (
                            input("URL: ")
                            or f"http://0.0.0.0:{self.__get_random_open_port()}"
                        )
                        url = parse.urlparse(url_raw)
                    except Exception:
                        print("Wrong url format")
                        continue

                    if (
                        url.port
                        and self._is_open_port(url.port)
                        and url.port not in self.__already_used_ports
                    ):
                        self.__already_used_ports.append(url.port)
                        break
                    else:
                        print(
                            "Port is not defined or used by another process. Try another or press 'Enter' to randomly choose open one"
                        )
                        continue

                while True:
                    try:
                        type = int(input("Type: "))
                    except ValueError:
                        print("Type should be an int value")
                        continue

                    if type < 0 or type >= 2:
                        print("Type can be only 0 or 1")
                        continue

                    break

                print()

                acc[template["name"]].append({"url": url, "type": type})

            return acc

        data = reduce(
            lambda acc, template: get_user_input(acc, template),
            (HLS_TEMPLATE, VODS_TEMPLATE, CODS_TEMPLATE),
            defaultdict(list),
        )

        print("Start building Fastocloud config...")
        self._build_fastocloud_config(host, alias, data, ml_version)
        print("Successfully build Fastocloud config")

        print("Start building NGINX configs for HLS, VODS, CODS...")
        self._build_nginx_config(data)
        print("Successfully build NGINX configs")

    def _build_fastocloud_config(
        self,
        host: str,
        alias: str,
        data: Dict[str, List[Dict[str, Any]]],
        ml_version: bool,
    ) -> None:
        template = FASTOCLOUD_PRO_ML_TEMPLATE if ml_version else FASTOCLOUD_PRO_TEMPLATE

        def config_template(node: Dict[str, Any]) -> Dict[str, str]:
            return {
                "host": node["url"].geturl(),
                "type": node["type"],
            }

        ports = {}
        for name, nodes in data.items():
            ports[name] = list(map(config_template, nodes))

        nodes = str(yaml.dump(ports))

        new_config = FASTOCLOUD_CONFIG_TEMPLATE.format(
            host=host, alias=alias, nodes=nodes
        )

        return self._write_fastocloud_config(template["filename"], new_config)

    def _write_fastocloud_config(self, filename: str, config: str) -> None:
        config_path = os.path.join(FASTOCLOUD_CONFIG_DIR, filename)

        with open(config_path, "w+") as f:
            f.write(config)

    def _build_nginx_config(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for template in (HLS_TEMPLATE, VODS_TEMPLATE, CODS_TEMPLATE):
            nodes = data[template["name"]]

            new_config = ""

            for node in nodes:
                port = node["url"].port
                port_string = self.__get_listen_port_string(port)

                server = NGINX_TEMPLATE.format(
                    access_log=template["access_log"].format(port=port),
                    error_log=template["error_log"].format(port=port),
                    listen_port=port_string,
                    alias=template["alias"],
                ).expandtabs(4)

                new_config += "\n" + server

            self._write_nginx_config(template["filename"], new_config)

    def _write_nginx_config(self, filename: str, config: str) -> None:
        available_path = os.path.join(NGINX_SITES_AVAILABLE_FOLDER, filename)
        enabled_path = os.path.join(NGINX_SITES_ENABLED_FOLDER, filename)

        with open(available_path, "w+") as available, open(
            enabled_path, "w+"
        ) as enabled:
            enabled.write(config)
            available.write(config)

    def __get_random_open_port(self) -> int:
        while True:
            port = random.randrange(1, 65536)
            if self._is_open_port(port) and port not in self.__already_used_ports:
                return port

    def __get_listen_port_string(self, port: int) -> str:
        return f"listen {port};\n\tlisten [::]:{port};\n"


if __name__ == "__main__":
    app = CdnConfigBuilder()
    app.run()
