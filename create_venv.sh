#!/bin/bash

put() {
    echo "---------------------------------"
    echo "$@"
    echo "---------------------------------"
}

mainline_scapy() {
    cd /tmp
    git clone "https://github.com/secdev/scapy.git"
    cd "scapy"
    python3 "setup.py" install
    cd ..
    \rm -rfv "scapy" #rm is often aliased to rm -i
}

install() {
    #install ansible
    pip3 install "ansible"

    #install scapy
    mainline_scapy

    #install ipython for scapy
    pip3 install "ipython"
}

if [[ -d "venv" ]]; then
    put "deleting current virtual environment"
    \rm -rv "venv"
fi

put "creating empty venv"
mkdir -v "venv"
python3 -m venv venv

if [[ -d "venv" ]]; then
    put "activating new venv"
    source "venv/bin/activate"

    put "installing dependencies into new venv"
    install
else
    put "error: directory venv not there"
    exit 1
fi