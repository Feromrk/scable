 
#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: uds_scanner

short_description: Scans for UDS sessions and services on a bus.

description:
    - Uses the provided sockets for the underlying ISOTP communication.
    - Tries to discover available UDS services and UDS sessions.
    - Very limited features yet, since the underlying scapy UDSScanner is currently in development.
    - Only scans for services and sessions in the DefaultSession and stops afterwards.

options:
    reset_handler:
        description:
            - Get this option from the output of module M(ecu_switch).
            - Currently ignored.
        type: dict
        required: no

    session_range:
        description:
            - Sets the last session id to be scanned.
            - Always starts at 0.
        type: int
        default: 0x100      

extends_documentation_fragment: [ isotp_sockets, debug, out_file ]

seealso:
    - name: Unified Diagnostic Services
      description: Reference of the UDS protocol
      link: https://en.wikipedia.org/wiki/Unified_Diagnostic_Services

requirements:
    - scapy   
    - paramiko

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

- name: uds scan
  uds_scanner:
    isotp_sockets: {{ udssocks.sockets }}
    session_range: 5
    out_file: /tmp/uds_scan_result.txt
'''

RETURN = '''
changed:
    description: 
      - Indicates whether the target state was changed. 
      - Since uds scans may change the target ecu state, this is set to true when a scan was triggered.
    type: bool
    returned: always
found_services:
    description: 
      - Amount of found services.
    type: int
    returned: always
found_sessions:
    description: 
      - Amount of found sessions.
    type: int
    returned: always
'''
import traceback 
import os
import json
import contextlib

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    import ansible.module_utils.scapy as scapy_utils
    HAS_SCAPY = True
except:
    HAS_SCAPY = False
    SCAPY_IMP_ERR = traceback.format_exc()

#make the single ansible module object global so that all functions can reach it
module = None

def fail_on_missing_option(**kwargs):
    for option_name, option_value in kwargs.items():
        if not option_value:
            module.fail_json(msg="missing option '{}'".format(option_name))

def run_module():
    global module

    module_args = {
        'reset_handler': {
            'type': 'dict',
            'required': False
        }, 
        'session_range': {
            'type': int,
            'default': 0x100
        },
        'isotp_sockets': {
            'type': 'list', 
            'elements': 'dict', 
            'required': True
        },
        'debug': {
            'type': 'bool',
            'default': False
        },
        'out_file': {
            'type': 'str'
        }
    }

    result = {
        'changed': False,
        'found_sessions': 0,
        'found_services': 0
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    reset_handler = module.params.get('reset_handler') #not used yet
    isotp_sockets = module.params['isotp_sockets']
    session_range = module.params['session_range']
    debug = module.params['debug']
    out_file = module.params.get('out_file')

    #check if all dependencies are there
    if not HAS_SCAPY:
        module.fail_json(msg=missing_required_lib("scapy"), exception=SCAPY_IMP_ERR)

    if module.check_mode:
        module.exit_json(**result)

    scapy_utils.init(ansible_module=module, debug=debug)

    #load scapy with isotp + uds features
    scapy_utils.load_scapy(isotp=True, uds=True)

    #deserialize sockets into real scapy objects
    isotp_sockets_objects = scapy_utils.isotp.load_socks(isotp_sockets)


    if out_file:
        #recursively create all needed directories
        dirname = os.path.dirname(out_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    #TODO: wait until nils' uds scanner is done and use it here
    #the steps done here are only a small subset of all the steps from the real uds scanner that is beeing developed currently
    try:
        #redirect stdout/stderr if we are going to write to it
        with scapy_utils.std_redirected(out_file) if out_file else contextlib.nullcontext():
                
            if out_file:
                print("===============================================")
                print("MODULE: uds_scanner\n")

            scapy_utils.debug("starting uds scans")

            for i, sock in enumerate(isotp_sockets_objects):
                scapy_utils.debug("socket {}/{}".format(i, len(isotp_sockets_objects)-1))

                scapy_utils.debug("Starting service scan")
                found_services = UDS_ServiceEnumerator(sock)

                result['found_services'] += len(found_services)

                if out_file:
                    print("------------------------------------------------------")
                    print("Scanning on ISOTP socket:\n {}".format(json.dumps(isotp_sockets[i], indent=4)))
                    print("UDS_SERVICE_SCAN_RESULTS")
                    make_lined_table(found_services, getTableEntry)

                scapy_utils.debug("Starting session scan")
                found_sessions = UDS_SessionEnumerator(sock, session_range=range(0, session_range))

                result['found_sessions'] += len(found_sessions)

                if out_file:
                    print("UDS_SESSION_SCAN_RESULTS")
                    for s in found_sessions:
                        s.show()
    except IOError:
        module.fail_json(msg="could not write to out_file", exception=traceback.format_exc())


    result['changed'] = True

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