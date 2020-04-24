from scapy.all import *
from scapy.layers.can import *
import threading


conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': True}
conf.contribs['CANSocket'] = {'use-python-can': False}

load_contrib('isotp')
load_contrib('automotive.uds')
load_contrib('automotive.ecu')
load_contrib('cansocket')

can_iface = 'vcan0'

sock1 = ISOTPSocket(can_iface, sid=0x701, did=0x601, basecls=UDS)

responseList = [ECUResponse(session=range(255), security_level=range(255), responses=UDS() / UDS_ERPR(resetType='hardReset')),
                ECUResponse(session=range(255), security_level=range(255), responses=UDS() / UDS_DSCPR(diagnosticSessionType=0x01)),
                ECUResponse(session=range(255), security_level=range(255), responses=UDS() / UDS_DSCPR(diagnosticSessionType=0x02)),
                ]

answering_machine1 = ECU_am(supported_responses=responseList, main_socket=sock1, basecls=UDS, timeout=None)

sim1 = threading.Thread(target=answering_machine1)

sim1.start()