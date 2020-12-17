#!/bin/bash
set -ex

# exports
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig

# variables
USER=fastocloud

# update system
apt-get update
apt-get install -y git python3-setuptools python3-pip --no-install-recommends

# install pyfastogt
git clone https://github.com/fastogt/pyfastogt
cd pyfastogt
python3 setup.py install
cd ../
rm -rf pyfastogt

# build env for service
./build_fastocloud_lb_env_from_repo.py --without-fastotv-cpp

# add user
useradd -m -U -d /home/$USER $USER -s /bin/bash
