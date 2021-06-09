# NaturalComputation2021-contest

## PARAMETERS & RESULTS
* il file **trained_params/logs_10_gen** è quello da cui siamo partiti
* Il file **trained_params/logs_45_gen_2** è quello ottenuto con la fitness classica VxV-dxd in cui la penalty è scalata di 10
* Il file **trained_params/logs_32_gen_3** contiene i migliori risultati relativi all'addestramento fatto senza avversari, in cui la penalty è stata scalata di 100 per favorire la velocità.
* Il file **trained_params/logs_20_gen_7** contiene i risultati relativi all'unico addestramento fatto con gli avversari.

**N.B**: : cercare di rigenerare risultati relativi all'addestramento fatto con check_pos (sensore trackPos) se serve per la relazione

## CLIENT & SNAKEOIL
In [client.py](client.py) la funzione principale è race a cui va passata la porta su cui deve connettersi il client e il dizionario di parametri che deve usare. Aggiunto controllo per supportare le modifiche fatte in [snakeoil.py](snakeoil.py).

In [snakeoil.py](snakeoil.py) abbiamo modificato la funzione *get_servers_input()* aggiungendo dei return True o False a seconda se l'operazione in questione è andata a buon fine o meno; questo perchè con gli avversari abbiamo avuto dei problemi di connessione col server che o chiudeva (secondo if) o non mandava i dati (primo if)

## FUNZIONE DI FITNESS
Partendo dai parametri trovati senza avversari, allenare con una fitness semplice che incentivi a superare per arrivare in prima posizione (racePos e opponents) e poi intodurre damage.