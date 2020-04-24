#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: detect_uds_sockets

short_description: Iterate over a list of ISOTPSockets and detect whether the socket also supports UDS

description:
    - Iterates over a provided list of ISOTPSockets and sends UDS messages to detect whether the device behind the socket supports the UDS protocoll.
    - The sent UDS messages request the ECU Reset Service by default, which should be implemented by most ECUs.
    - Listens for a positive response (request SID + 0x40) or a negative response (SID 0x7f).

options:
    isotp_sockets:
        description:
            - These ISOTPSockets are used for communication with ECUs.
            - Scapy ISOTPSockets are created internally from the information provided here.
            - Can be created by the module M(isotp_scanner)
        required: true
        type: list
        elements: dict
    service: 
        description:
            - The UDS service to be requested from the ECU.
            - Default is SID 0x11 -> ECU Reset
        type: str
        choices: ['ecu_reset']
        default: ecu_reset
    reset_type:
        description:
            - Needed if I(service=ecu_reset).
            - Reset type to be requested from the ECU.
        choices:['hard_reset', 'soft_reset']
        default: hard_reset

extends_documentation_fragment: [ debug, out_file ]

requirements:
    - scapy    

author:
    - Johannes Stark (@Feromrk)
'''

EXAMPLES = '''
- name: scan for isotp sockets
  isotp_scanner:
    interface: can1
    register: isotpsocks
- name: test found sockets to get UDS sockets
    detect_uds_sockets:
      isotp_sockets: "{{ isotpsocks.sockets }}"
    register: udssocks
'''

RETURN = '''
sockets:
    description: A list of found UDS sockets
    type: list
    elements: dict
    returned: always
    contains: 
        interface:
            description: the interface for the socket
            type: str
            returned: on scan success
        sid:
            description: source id
            type: str
            returned: on scan success
        did:
            description: destination id
            type: str
            returned: on scan success
        extended_addr:
            description: extended_addr
            type: str
            returned: on scan success
        extended_rx_addr:
            description: extended_rx_addr
            type: str
            returned: on scan success
        padding:
            description: padding
            type: bool
            returned: on scan success
        listen_only:
            description: listen_only
            type: bool
            returned: on scan success
        basecls:
            description: base class
            type: str
            returned: on scan success
'''

import traceback 
import json
import time
import os

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

SCAPY_IMP_ERR = None
try:
    import ansible.module_utils.scapy as scapy_utils
    HAS_SCAPY = True
except:
    HAS_SCAPY = False
    SCAPY_IMP_ERR = traceback.format_exc()

def get_scapy_reset_type(reset_type):
    scapy_reset_type = 'hardReset'

    if reset_type == 'soft_reset':
        scapy_reset_type = 'softReset'
    
    return scapy_reset_type

def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = {
        'isotp_sockets': {
            'type': 'list', 
            'elements': 'dict', 
            'required': True
        },
        'service': {
            'type': 'str', 
            'required': False, 
            'choices': ['ecu_reset'], 
            'default': 'ecu_reset'
        },
        'reset_type': {
            'type': 'str', 
            'default': 'hard_reset',
            'choices': ['hard_reset', 'soft_reset']
        },
        'debug': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'out_file': {
            'type': 'str'
        }
    }

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = {
        'changed': True,
        'sockets': []
    }

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_SCAPY:
        module.fail_json(msg=missing_required_lib("scapy"), exception=SCAPY_IMP_ERR)

    
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    isotp_sockets = module.params['isotp_sockets']
    service = module.params['service']
    reset_type = module.params['reset_type']
    debug = module.params['debug']
    out_file = module.params.get('out_file')

    scapy_utils.init(ansible_module=module, debug=debug)

    #load scapy with isotp + uds features
    scapy_utils.load_scapy(isotp=True, uds=True)

    #deserialize sockets into real scapy objects
    isotp_socks = scapy_utils.isotp.load_socks(isotp_sockets)
    result_socks = []

    scapy_utils.debug("Scapy sockets created: {}".format(isotp_socks))

    if(service == 'ecu_reset'):
        scapy_utils.debug("All isotp_socks: {}".format(isotp_socks))
        for s in isotp_socks:
            scapy_utils.debug("Socket: {}".format(vars(s)))

            s.basecls = UDS
            p = UDS()/UDS_ER(resetType=get_scapy_reset_type(reset_type))
            scapy_utils.debug("Sending packet {}".format(p.command()))
            resp = s.sr1(p, timeout=1, verbose=False)

            #try second time, in case ECU was waken up by first message
            if resp is None:
                time.sleep(3)
                resp = s.sr1(p, timeout=3, verbose=False)

            if resp is None:
                scapy_utils.debug("No response")
                continue
            scapy_utils.debug("Got response, service {}".format(resp.service))
            #SID of ECU_RESET is 0x11 -> answer is 0x51 or a negative response
            if resp.service in [0x51, 0x7f]:
                scapy_utils.debug("Found UDS Socket")
                time.sleep(1)
                result_socks.append(s)

    result['sockets'] = scapy_utils.isotp.dump_socks(result_socks)

    if out_file:
        #recursively create all needed directories
        dirname = os.path.dirname(out_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    
        with scapy_utils.std_redirected(out_file):
            print("===============================================")
            print("MODULE: detect_uds_sockets")
            print("found UDS sockets:")
            print("{}".format(json.dumps(result['sockets'], indent=4)))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()