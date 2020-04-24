import ansible.module_utils.scapy.core as c
from ansible.module_utils.scapy.errors import SerializationError, DeserializationError
__is_init = False

# ISOTPSoftSocket
# def __init__(self,
#              can_socket=None,
#              sid=0,
#              did=0,
#              extended_addr=None,
#              extended_rx_addr=None,
#              rx_block_size=0,
#              rx_separation_time_min=0,
#              padding=False,
#              listen_only=False,
#              basecls=ISOTP):
                
# ISOTPNativeSocket
# def __init__(self,
#         iface=None,
#         sid=0,
#         did=0,
#         extended_addr=None,
#         extended_rx_addr=None,
#         listen_only=False,
#         padding=False,
#         transmit_time=100,
#         basecls=ISOTP):


#allowed basecls classes in ISOTPSocket as a string representation
__BASECLS_OPTIONS = ['ISOTP', 'UDS']

#this map is for serialization of ISOTPSocket objects
#depending on the scapy config, it uses different underlaying classes ISOTPNativeSocket or ISOTPSoftSocket
#the key is the name of the parameter in the constructor, the value is the (nested) representation of how the value is stored internally in the object
ISOTPSOCKET_OPTIONS_MAP = {
    'sid': ['src'],
    'did': ['dst'],
    'extended_addr': ['exsrc'],
    'extended_rx_addr': ['exdst'],
    'padding': None,
    'listen_only': None,
    'basecls': None,
}

def __init():
    global __is_init

    if __is_init:
        return

    if(c.ISOTPSOCKET_IS_NATIVE):
        #ISOTPNativeSocket
        # >>> n = ISOTPNativeSocket('vcan0')                                              
        # >>> vars(n)                                                                     
        # {'iface': 'vcan0',
        # 'can_socket': <socket.socket fd=14, family=AddressFamily.AF_CAN, type=SocketKind.SOCK_DGRAM, proto=6, laddr=('', 0, 0)>,
        # 'src': 0,
        # 'dst': 0,
        # 'exsrc': None,
        # 'exdst': None,
        # 'ins': <socket.socket fd=14, family=AddressFamily.AF_CAN, type=SocketKind.SOCK_DGRAM, proto=6, laddr=('', 0, 0)>,
        # 'outs': <socket.socket fd=14, family=AddressFamily.AF_CAN, type=SocketKind.SOCK_DGRAM, proto=6, laddr=('', 0, 0)>,
        # 'basecls': scapy.contrib.isotp.ISOTP}

        c.debug("ISOTPSocket is ISOTPNativeSocket")
        ISOTPSOCKET_OPTIONS_MAP['iface'] = ['iface']
    else:
        #ISOTPSoftSocket
        # >>> s = ISOTPSoftSocket('vcan0')                                                
        # >>> vars(s)                                                                     
        # {'exsrc': None,
        # 'exdst': None,
        # 'src': 0,
        # 'dst': 0,
        # 'ins': <scapy.contrib.isotp.ISOTPSocketImplementation at 0x7fdd9525a700>,
        # 'outs': <scapy.contrib.isotp.ISOTPSocketImplementation at 0x7fdd9525a700>,
        # 'impl': <scapy.contrib.isotp.ISOTPSocketImplementation at 0x7fdd9525a700>,
        # 'basecls': scapy.contrib.isotp.ISOTP}

        # how does impl look like?
        # >>> vars(vars(s)['impl'])                                                       
        # {'hooks': [],
        # 'can_socket': <<CANSocket: read/write packets at a given CAN interface using PF_CAN sockets> at 0x7fdd951ee7f0>,
        # 'dst_id': 0,
        # 'src_id': 0,
        # 'padding': False,
        # 'fc_timeout': 1,
        # 'cf_timeout': 1,
        # 'filter_warning_emitted': False,
        # 'extended_rx_addr': None,
        # 'ea_hdr': b'',
        # 'listen_only': False,
        # 'rxfc_bs': 0,
        # 'rxfc_stmin': 0,
        # 'rx_queue': <queue.Queue at 0x7fdd9e4ab910>,
        # 'rx_len': -1,
        # 'rx_buf': None,
        # 'rx_sn': 0,
        # 'rx_bs': 0,
        # 'rx_idx': 0,
        # 'rx_state': 0,
        # 'txfc_bs': 0,
        # 'txfc_stmin': 0,
        # 'tx_gap': 0,
        # 'tx_buf': None,
        # 'tx_sn': 0,
        # 'tx_bs': 0,
        # 'tx_idx': 0,
        # 'rx_ll_dl': 0,
        # 'tx_state': 0,
        # 'tx_timer': <TimeoutThread(ISOTP Timer Thread-4, started 140589659567872)>,
        # 'rx_timer': <TimeoutThread(ISOTP Timer Thread-5, started 140589446199040)>,
        # 'rx_thread': <CANReceiverThread(CANReceiverThread-6, started 140589437806336)>,
        # 'tx_mutex': <unlocked _thread.lock object at 0x7fdd951f03c0>,
        # 'rx_mutex': <unlocked _thread.lock object at 0x7fdd951f0810>,
        # 'send_mutex': <unlocked _thread.lock object at 0x7fdd951f0e70>,
        # 'tx_done': <threading.Event at 0x7fdd951f07c0>,
        # 'tx_exception': None,
        # 'tx_callbacks': [],
        # 'rx_callbacks': []}

        #and finally can_socket
        # >>> vars(vars(vars(s)['impl'])['can_socket'])                                   
        # {'basecls': scapy.layers.can.CAN,
        # 'remove_padding': True,
        # 'iface': 'vcan0',
        # 'ins': <socket.socket fd=12, family=AddressFamily.AF_CAN, type=SocketKind.SOCK_RAW, proto=1, laddr=('vcan0',)>,
        # 'outs': <socket.socket fd=12, family=AddressFamily.AF_CAN, type=SocketKind.SOCK_RAW, proto=1, laddr=('vcan0',)>}

        #iface is a needed value for serialization

        c.debug("ISOTPSocket is ISOTPSoftSocket")
        ISOTPSOCKET_OPTIONS_MAP['can_socket'] = ['impl', 'can_socket', 'iface']

    __is_init = True



def __get_nested_value(socket, args):
    ''' 
        Read nested value in socket object.

        socket: ISOTPNativeSocket or ISOTPSoftSocket
        args: list of object attribute names which are nested

        example ISOTPSoftSocket:
    
        def __init__(self,
                     can_socket=None,
                     sid=0,
                     did=0,
                     extended_addr=None,
                     extended_rx_addr=None,
                     rx_block_size=0,
                     rx_separation_time_min=0,
                     padding=False,
                     listen_only=False,
                     basecls=ISOTP):

        ISOTPSoftSocket accepts can_socket as string / CANSocket object and stores the value in a nested structure
        consider this: s = ISOTPSoftSocket('vcan0') -> the value 'vcan0' is needed in order to serialize the ISOTPSoftSocket object
        it is stored like this:
            s.impl.can_socket.iface
        
        this functions recursively iterates over the socket object and calls vars() on every recursive step to get a dict representation of the object

        throws KeyError if nested args are not present in the object
    '''

    if args and socket:
        element  = args[0]
        if element:
            value = vars(socket)[element]
            return value if len(args) == 1 else __get_nested_value(value, args[1:])
 


def dump_socks(socks, throw=False):
    '''
        Serialize list of ISOTPSocket objects into a list of dicts.

        socks: List of ISOTPSocket objects to be serialized.
        throw: If this is set to True this function will throw a SerializationError on a failed serialization.
    '''

    __init()

    result = []
    c.debug("dump_socks")
    c.debug("socks:{}".format(socks))
    

    for sock in socks:
        
        #check for right types
        assert(isinstance(sock, (ISOTPNativeSocket, ISOTPSoftSocket)))
        if isinstance(sock, ISOTPNativeSocket):
            assert(c.ISOTPSOCKET_IS_NATIVE)
        elif isinstance(sock, ISOTPSoftSocket):
            assert(not c.ISOTPSOCKET_IS_NATIVE)

        #options dict
        options = {}

        try:
            for key, value in ISOTPSOCKET_OPTIONS_MAP.items():
                options[key] = __get_nested_value(sock, value)
        except KeyError as e:
            error_str = "failed to serialize object '{}'. \
                    The object does not have the property you are looking for: '{}'".format(sock, repr(e))
            if(throw):
                raise SerializationError(error_str)
            else:
                c.warn(error_str)
                c.debug("object vars: {}".format(vars(sock)))
                continue

        # TODO get somehow:
        options['padding'] = True
        options['listen_only'] = False

        # get the scapy basecls
        # defaults to ISOTP on KeyError
        basecls = vars(sock).get('basecls', 'ISOTP').__name__
        if not basecls in __BASECLS_OPTIONS:
            error_str = "failed to serialize object: {}. unknown basecls: {}".format(sock, basecls)
            if(throw):
                raise SerializationError(error_str)
            else:
                c.warn(error_str)
                c.debug("object vars: {}".format(vars(sock)))
                continue
        
        options['basecls'] = basecls
        
        result.append(options)

    c.debug("serialized ISOTPSockets:{}".format(result))

    return result

def load_socks(socks, throw=False):
    '''
        Deserialize list of dicts into list of ISOTPSocket objects.
        Each key:value pair of the dict is directly passed to the constructor of the ISOTPSocket object.
        All keys must be accepted by the constructor. Otherwise the deserialization fails.

        socks: List of dicts (ISOTPSocket objects that were serialized earlier) to be deserialized into scapy objects.
        throw: If this is set to True this function will throw a DeserializationError on a failed deserialization.
    '''

    __init()

    result = []

    c.debug("socks:{}".format(socks))

    for sock in socks:

        #check format of sock
        #if key is not found in the default layout raise an error
        for key in sock:
            if key not in ISOTPSOCKET_OPTIONS_MAP:
                error_str = "Wrong key '{}' in socket '{}'".format(key, sock)
                if(throw):
                    raise DeserializationError(error_str)
                else:
                    c.warn(error_str)
                    c.debug("object vars: {}".format(vars(sock)))
                    continue

        basecls_string = sock.pop('basecls')

        #check if basecls is correct
        if basecls_string not in __BASECLS_OPTIONS:
            error_str = "Unknown basecls '{}' in socket '{}'".format(basecls_string, sock)
            if(throw):
                raise DeserializationError(error_str)
            else:
                c.warn(error_str)
                c.debug("object vars: {}".format(vars(sock)))
                continue

        if basecls_string == 'UDS':
            basecls = UDS
        else:
            basecls = ISOTP

        try:
            if c.ISOTPSOCKET_IS_NATIVE:
                s = ISOTPNativeSocket(
                        **sock,
                        basecls=basecls
                )
            else:
                s = ISOTPSoftSocket(
                        **sock,
                        basecls=basecls
                )
        except TypeError as e:
            error_str = "Unknown value passed to constructor '{}' in socket '{}'".format(repr(e), sock)
            if(throw):
                raise DeserializationError(error_str)
            else:
                c.warn(error_str)
                c.debug("object vars: {}".format(vars(sock)))
                continue

        result.append(s)
    
    return result