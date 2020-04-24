class ModuleDocFragment(object):
    DOCUMENTATION = r'''
    options:
        isotp_sockets:
            description:
                - A list of serialized isotp_socket objects.
                - Can be created by the module M(isotp_scanner) or manually.
                - A Scapy ISOTPSocket is created internally from the information provided here.
                - The ISOTPSockets are used for the communication with ECU.
            required: true
            type: list
            elements: dict
            suboptions: 
                interface:
                    description: the interface for the socket
                    type: str
                sid:
                    description: source id
                    type: str
                did:
                    description: destination id
                    type: str
                extended_addr:
                    description: extended_addr
                    type: str
                extended_rx_addr:
                    description: extended_rx_addr
                    type: str
                padding:
                    description: padding
                    type: bool
                listen_only:
                    description: listen_only
                    type: bool
                basecls:
                    description: base class
                    type: str
    '''