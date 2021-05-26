# Importazione delle librerie Python.
import os
from threading import Thread

# Definizione della classe Server con supporto per il multithreading.
class Server(Thread):
    # Inizializzatore, prende in ingresso il nome del tracciato.
    def __init__(self, track):
        self.track = track
        print ("Server {} partito".format(track))
        Thread.__init__(self)

    # Metodo che avvia il server.
    # Richiama l'istruzione per l'avvio del server da linea di comando.
    # E' necessaria una configurazione preliminare delle directory di TORCS e del
    # file di configurazione della corsa.
    def run(self):
        os.system(
            r"pushd E:\torcs_{} & wtorcs.exe -nofuel -nodamage -nolaptime -T -t 1000000000 "
            r".\config\raceman\quickrace.xml >NUL".format(self.track))
