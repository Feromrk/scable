#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: isotp_scanner

short_description: Scan for ISOTP Sockets on a bus and return findings.

description:
    - Uses scapy's ISOTPScan() to scan the connected CAN bus on a provided interface.
    - May take a lot of time depending on the scan range.

seealso:
    - name: Scapy ISOTPScan
      description: Official reference to the scapy ISOTPScan function used here
      link: https://scapy.readthedocs.io/en/latest/api/scapy.contrib.isotp.html#scapy.contrib.isotp.ISOTPScan

options:
    interface:
        description:
            - This is the interface that is used for scanning.
        required: true
    scan_range_start: 
        description:
            - A range of CAN-Identifiers is scanned.
            - This option sets the starting ID.
        type: int
        default: 0x0
    scan_range_end: 
        description:
            - A range of CAN-Identifiers is scanned.
            - This option sets the ending ID.
        type: int
        default: 0x7ff

extends_documentation_fragment: [ debug, out_file ]

requirements:
    - scapy    

author:
    - Johannes Stark (@Feromrk)
'''

EXAMPLES = '''
- name: Scan with default range
  isotp_scanner:
    interface: can1

- name: Test with a message and changed output
  isotp_scanner:
    interface: can1
    scan_range_end: 0xf

'''

RETURN = '''
sockets:
    description: A list of found sockets
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

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


SCAPY_IMP_ERR = None
try:
    import ansible.module_utils.scapy as scapy_utils
    HAS_SCAPY = True
except:
    HAS_SCAPY = False
    SCAPY_IMP_ERR = traceback.format_exc()

#make the ansible module object global so that all functions can reach it
module = None

def run_module():
    global module

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        interface=dict(type='str', required=True),
        scan_range_start=dict(type='int', required=False, default=0x0),
        scan_range_end=dict(type='int', required=False, default=0x7ff),
        debug=dict(type='bool', required=False, default=False),
        out_file=dict(type='str')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=True,
        sockets=list()
    )

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

    interface = module.params['interface']
    scan_range_start = module.params['scan_range_start']
    scan_range_end = module.params['scan_range_end']
    debug = module.params['debug']
    out_file = module.params.get('out_file')

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    scapy_utils.init(ansible_module=module, debug=debug)

    scapy_utils.debug("loading scapy")
    scapy_utils.load_scapy(isotp=True)

    scapy_utils.debug("starting isotpscan")
    socks = ISOTPScan(
        CANSocket(interface), 
        range(scan_range_start, scan_range_end),
        False,
        noise_listen_time=5,
        verbose=False,
        can_interface=interface,
        output_format='sockets'
    )

    result['sockets'] = scapy_utils.isotp.dump_socks(socks)

    if out_file:
        #recursively create all needed directories
        dirname = os.path.dirname(out_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    
        with scapy_utils.std_redirected(out_file):
            print("===============================================")
            print("MODULE: isotp_scanner")
            print("found ISOTP sockets:")
            print("{}".format(json.dumps(result['sockets'], indent=4)))

    module.exit_json(**result)

def main():
    try:
        run_module()
    #do not catch normal SystemExit from module.exit_json()
    except SystemExit as e:
        if e.code == 0:
            raise e
    except:
        module.fail_json(msg="unhandled exception", exception=traceback.format_exc())
        

if __name__ == '__main__':
    main()