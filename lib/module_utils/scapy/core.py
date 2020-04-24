import sys, os
import contextlib
from scapy.all import conf, load_contrib, load_layer
from scapy.main import _load
from ansible.module_utils.consts import LINUX, WINDOWS
from ansible.module_utils.six import PY3

ANSIBLE_MODULE = None
ISOTPSOCKET_IS_NATIVE = False

__DEBUG = False
__INIT = False

def __linux_kernel_module_loaded(kernel_module_name):
    '''Checks if a kernel module is loaded in linux.'''

    rc, stdout, _ = ANSIBLE_MODULE.run_command(['lsmod'])
    rc, stdout, _ = ANSIBLE_MODULE.run_command(['grep', kernel_module_name], data=stdout)
    
    return rc == 0


def init(ansible_module=None, debug=False):
    '''
        Initialize scapy_utils with the ansible module and additional flags.
        This function must be called prior to using any other features.
    '''

    global ANSIBLE_MODULE, __DEBUG, __INIT

    if not PY3:
        sys.exit("python version is not 3")

    if ansible_module is not None:
        ANSIBLE_MODULE = ansible_module
    else:
        raise TypeError("ansible_module must not be None")

    if isinstance(debug, bool):
        __DEBUG = debug

    __INIT = True


def debug(msg):
    '''
        Used for printing out debugging messages via the journal.
        Can be enabled with flags passed to the init() function.
    '''
    if __DEBUG:
        ANSIBLE_MODULE.log("DEBUG '{}' in '{}': {}".format(
            sys._getframe(1).f_code.co_name, 
            os.path.basename(sys._getframe(1).f_code.co_filename),
            msg)
        )

def warn(msg):
    '''
        Used for printing out warnings via the journal.
        Can not be disabled.
    '''
    ANSIBLE_MODULE.log("WARNING: " + msg)


def load_scapy(isotp=True, uds=False):
    '''
        Initializes scapy for the use within the custom ansible module.
        Loads needed scapy modules and makes them directly available in the global namespace.
    '''
    global ISOTPSOCKET_IS_NATIVE
    
    if not __INIT:
        raise RuntimeError("init() was not called")

    if(WINDOWS):
        debug("Platform is Windows -> CANSocket is python-can, ISOTPSocket is ISOTPSoftSocket")

        conf.contribs['CANSocket'] = {'use-python-can': True}
        conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': False}

    elif(LINUX):
        debug("Platform is Linux -> CANSocket is native")
        conf.contribs['CANSocket'] = {'use-python-can': False}

        if(__linux_kernel_module_loaded('can_isotp')):
            debug("using can_isotp kernel module")
            conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': True}
            ISOTPSOCKET_IS_NATIVE = True
        else:
            debug("can_isotp kernel module not loaded")
            conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': False}
            ISOTPSOCKET_IS_NATIVE = False

        load_contrib("cansocket")
        load_layer("can")

    if(isotp):
        load_contrib("isotp")

    if(uds):
        load_contrib("automotive.uds")

    _load("scapy.utils")

def is_basic_type(object):
    return ( isinstance(object, str)
        or isinstance(object, int) 
        or isinstance(object, float) 
        or isinstance(object, bool) 
    )

def object_to_dict(object):
    '''
        Serialize an object to a dict using vars().
        Complex types and attributes starting with a '_' are skipped.
    '''
    result = {}

    for attribute, value in vars(object).items():
        if ( isinstance(attribute, str)  
            and not attribute.startswith('_') 
            and is_basic_type(value) ):

            result[attribute] = value
    
    return result


@contextlib.contextmanager
def std_redirected(filename):
    '''
    A context manager to temporarily redirect stdout and stderr to filename

    e.g.:

    with std_redirected('testfile.txt'):
        print('hi')
    '''
    debug("redirecting stdout/stderr to '{}'".format(filename))

    try:
        old_stdout = os.dup(sys.stdout.fileno())
        old_stderr = os.dup(sys.stderr.fileno())

        f = open(filename, 'a')

        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

        yield
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        
        if old_stdout is not None:
            os.dup2(old_stdout, sys.stdout.fileno())
        if old_stderr is not None:
            os.dup2(old_stderr, sys.stderr.fileno())
        if f is not None:
            f.close()