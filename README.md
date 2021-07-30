# NaturalComputation2021-contest

## PARAMETERS & RESULTS
* il file **trained_params/logs_10_gen** è quello da cui siamo partiti
* Il file **trained_params/logs_45_gen_2** è quello ottenuto con la fitness classica VxV-dxd in cui la penalty è scalata di 10
* Il file **trained_params/logs_32_gen_3** contiene i migliori risultati relativi all'addestramento fatto senza avversari, in cui la penalty è stata scalata di 100 per favorire la velocità.
* Il file **trained_params/logs_20_gen_7** contiene i risultati relativi all'unico addestramento fatto con gli avversari.

**N.B**: : cercare di rigenerare risultati relativi all'addestramento fatto con check_pos (sensore trackPos) se serve per la relazione

Togliere 20 all'inizio e 7 alla fine di 145_gen_4

## CLIENT & SNAKEOIL
In [client.py](client.py) la funzione principale è race a cui va passata la porta su cui deve connettersi il client e il dizionario di parametri che deve usare. Aggiunto controllo per supportare le modifiche fatte in [snakeoil.py](snakeoil.py).

In [snakeoil.py](snakeoil.py) abbiamo modificato la funzione *get_servers_input()* aggiungendo dei return True o False a seconda se l'operazione in questione è andata a buon fine o meno; questo perchè con gli avversari abbiamo avuto dei problemi di connessione col server che o chiudeva (secondo if) o non mandava i dati (primo if); tuttavia per lanciare il test dobbiamo commentare il return false del primo if

## FUNZIONE DI FITNESS
Partendo dai parametri trovati senza avversari, allenare con una fitness semplice che incentivi a superare per arrivare in prima posizione (racePos e opponents) e poi intodurre damage.

## FITNESS USATE
* SENZA AVVERSARI
  * 1e - 40 generazioni (_2) => **f = -(V1\*V2 - (D1-L1)\*(D2-L2)/100)** 
  * 2e - 150 generazioni (_3+_4) => **f = -(V1\*V2 - (D2-L2)\*(D2-L2)/1000)**
* CON AVVERSARI
  * 3e - 67 generazioni (_gen_exp3_)=> **f=-((F1_points(racePos1)+F1_points(racePos1))*10-(t1+t2)*10 -(damage1+damage2))** . Nel config partiamo in ultima posizione. Addestramento su tutti e quattro i circuiti (vecchia versione), dovremmo rifarlo con solo due circuiti (Forza e Wheel). Addestramento partito dal secondo esperimento. NOTE: Aggiunta di **damage** ma senza migliorie. Prova con **un solo circuito contemporaneamente** ma senza migliorie (_opponentsF1_2).
  * 4e - 67 generazioni (trained_params_67_gen_opponents_1) => **f = -((F1_points(racePos1)+F1_points(racePos1))*10 + (distRaced_1/time_1+distRaced_2/time_2)*10 - (damage1+damage2))** . Nel config partiamo in ultima posizione. Solo due circuiti (Forza e Wheel). Solo 5 avversari. Addestramento partito dal secondo esperimento.
  * 5e - 60 generazioni (trained_params_60_gen_opponents_2) => **f = stessa fitness dell'esperimento precedente**. Nel config partiamo in 4a posizione.  Solo due circuiti (Forza e Wheel). Addestramento partito dal secondo esperimento.
  * 5e - 127 generazioni (trained_params_127_gen_opponents_3) da sommare a quello precedente => **f = stessa fitness dell'esperimento precedente**. Nel config partiamo in 4a posizione.  Solo due circuiti (Forza e Wheel). Addestramento continua dall'esperimento precedente.
  * 6e - 100 generazioni (trained_params_{}_gen_opponents_4) => **f = stessa fitness dell'esperimento precedente**. Nel config partiamo in ultima posizione (9).  Solo due circuiti (Forza e Wheel). Addestramento partito dal secondo esperimento.
