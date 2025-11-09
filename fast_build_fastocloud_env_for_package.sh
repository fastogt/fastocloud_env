#!/bin/bash
set -ex

# exports
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
export DEBIAN_FRONTEND=noninteractive

# variables
USER=fastocloud

# update system
if [[ "$OSTYPE" == "linux-gnu" ]]; then
    if [ -n "$(command -v yum)" ]; then
      yum update -y
      yum install -y git python3-setuptools python3-pip rpm
    elif [ -n "$(command -v apt-get)" ]; then
      apt-get update
      apt-get install -y git python3-setuptools python3-pip rpm --no-install-recommends
    else
:
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
:
elif [[ "$OSTYPE" == "cygwin" ]]; then
:
elif [[ "$OSTYPE" == "msys" ]]; then
    pacman -Suy
    pacman -S --need --noconfirm ca-certificates git python3-setuptools python3-pip
:
elif [[ "$OSTYPE" == "win32" ]]; then
:
elif [[ "$OSTYPE" == "freebsd"* ]]; then
:
else
:
fi

# install pyfastogt
git clone https://gitlab.com/fastogt/pyfastogt
cd pyfastogt
pip3 install --break-system-packages .
cd ../
rm -rf pyfastogt

# build env for service
./build_fastocloud_env_from_repo.py "$@"

# add user
if ! id "$USER" &>/dev/null; then
    useradd -m -U -d /home/$USER $USER -s /bin/bash
fi
usermod -a -G video $USER
