## CLASSE PER CREARE THREAD NON DAEMON USANDO LA LIBRERIA POOL ##
# utile se vogliamo parallelizzare perchè la classe Pool non permette di avere altri figli, quindi si deve istanziare CustomPool

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
