# Scable
Scable is a proof of concept that implements automotive security tests (written in Python with [Scapy](https://github.com/secdev/scapy)) as [Ansible Modules](https://github.com/ansible/ansible). The goal was to demonstrate module based security testing. 

## Requirements
- Linux (Debian, Ubuntu, Manjaro etc.)
- [SocketCAN](https://en.wikipedia.org/wiki/SocketCAN) driver, which is available on modern Linux distributions
- [can_isotp](https://github.com/hartkopp/can-isotp) kernel module
- `python3`, `pip3`, `venv`; on debian based systems just execute `sudo apt-get install python3 python3-pip python3-venv`

## Installation
Execute `create_venv.sh` after installing the requirements. This script will create a virtual environment in the current directory and install all further requirements (ansible, scapy) into the venv.

## Documentation
All Ansible Modules must provide a documentation, which is accessible via `ansible-doc -t module [moduleName]`. (Note: setup environment first; see "Usage" down below.)

Valid module names are:
- isotp_scanner
- detect_uds_sockets
- uds_scanner

## Tests
There are unit and integration tests available. Every Module has a folder starting with test_* next to its implementation, which contains those tests. They can be executed with the script `run_test.sh`.

## Usage
- First execute `source source_me` to setup the environment in bash. 
- Create an Ansible Playbook, which uses the implemented Ansible Modules under `lib/modules`. Examples can be found under `test-system`, which includes system tests for a specific hardware setup (probably not yours).
- Run the playbook: `ansible-playbook [yourPlaybookName.yml] -vvv`