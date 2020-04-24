#!/bin/bash
trap "kill 0" EXIT

sudo ip link set down vcan0

if [[ ! $(lsmod | grep vcan) ]]; then 
    sudo modprobe vcan
fi

if [[ ! $(lsmod | grep can_isotp) ]]; then 
    sudo modprobe can_isotp
fi

sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

python3 ecu_am.py &
ansible-playbook testmod.yml
#sleep 30
