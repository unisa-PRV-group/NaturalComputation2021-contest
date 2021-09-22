import os
from threading import Thread,Event
import wmi
import platform
import subprocess
import signal

# Definizione della classe Server con supporto per il multithreading.
class Server(Thread):
    # Inizializzatore, prende in ingresso il nome del tracciato.
    def __init__(self, track):
        self.track = track
        self._stopper = Event()
        self.f=wmi.WMI()
        print ("\nServer {} partito".format(track))
        Thread.__init__(self)

    # metodo per chiudere il thread e uccidere il processo wtorcs.exe (occhio che uccide tutti quelli con questo nome)
    # kill è un booleano da passare solo se siamo sicuri che il processo non è stato ucciso da un altro, altrimenti dà errore
    def stop(self, kill=False):
        self._stopper.set()
        if kill:
            if platform.system()=="Linux":
                proc = subprocess.Popen(["pgrep", "wtorcs"], stdout=subprocess.PIPE)
                for pid in proc.stdout:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    # Check if the process that we killed is alive.
                    except: pass
            else:
                try:
                    for process in self.f.Win32_Process():
                        if process.name == "wtorcs.exe":
                            process.Terminate()
                except: pass

    # Metodo che avvia il server. Richiama l'istruzione per l'avvio del server da linea di comando.
    # E' necessaria una configurazione preliminare delle directory di TORCS e del file di configurazione della corsa.
    def run(self):
        os.system(
            r"pushd C:\Torcs_Competition\torcs_{} & wtorcs.exe -nofuel -nolaptime -T -t 1000000000 "
            r".\config\raceman\quickrace.xml >NUL".format(self.track))
