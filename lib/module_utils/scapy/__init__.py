'''
    make core functions directly available

    usage: import ansible.module_utils.scapy as scapy_utils
    scapy_utils.init(ansible_module=module)
'''
from .core import *


'''
    make isotp functions available via the isotp namespace

    usage: import ansible.module_utils.scapy as scapy_utils
    scapy_utils.isotp.dump_socks(isotp_socks)
'''
from . import isotp