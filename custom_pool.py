import multiprocessing
from multiprocessing.pool import Pool
from multiprocessing import Process

class NoDaemonProcess(Process):
    # make 'daemon' attribute always return False
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass

class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

class CustomPool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(CustomPool, self).__init__(*args, **kwargs)
