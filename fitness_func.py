from multiprocessing.pool import Pool
from client import race
import math
from Server import Server
import os
import json
import numpy as np

# path utili
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")

# recupero nome parametri
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
params={k:-1 for k in lb.keys()}

def fitness_alone(ind, ports, s1,s2, couple):
    for i,k in enumerate(params.keys()):
        params[k]=ind[i] # recupero valori dei parametri usando l'individuo ind

    # creo 2 clients sui due circuiti avviati
    with Pool(2) as p:
        results=p.starmap(race, [(ports[0],params),(ports[1],params)])
        distRaced_1,time_1,length_1,pos1,damage1,_ = results[0]
        distRaced_2,time_2,length_2,pos2,damage2,_ = results[1]
        del results

    # tempo=0 vuol dire c'e stato un errore
    if time_1==0 or time_2==0: # or distRaced_1<length_1 or distRaced_2<length_2:
        f=math.inf

        # riavvio servers
        s1.stop(True)
        s2.stop()
        
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()
    else:
        # calcolo fitness
        penalty_1 = distRaced_1-length_1
        penalty_2 = distRaced_2-length_2
        penalty = (penalty_1*penalty_2 + (damage1*damage2))/100
        vel = (distRaced_1/time_1)*(distRaced_2/time_2)
        f=-(vel-penalty)
    return f

f1_scores = [25, 18, 15, 12, 10, 8, 6, 4, 2]

def fitness_opponents_v2(ind, ports, s1,s2, couple):
    for i,k in enumerate(params.keys()):
        params[k]=ind[i] # recupero valori dei parametri usando l'individuo ind

    # creo 2 clients sui due circuiti avviati
    with Pool(2) as p:
        results=p.starmap(race, [(ports[0],params),(ports[1],params)])
        distRaced_1,time_1,length_1,pos1,damage1,_ = results[0]
        distRaced_2,time_2,length_2,pos2,damage2,_ = results[1]
        del results

    # tempo=0 vuol dire c'e stato un errore
    if time_1==0 or time_2==0: # or distRaced_1<length_1 or distRaced_2<length_2:
        f=math.inf

        # riavvio servers
        s1.stop(True)
        s2.stop()
        
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()
    else:
        # calcolo fitness
        f = -((f1_scores[int(pos1)-1]+f1_scores[int(pos2)-1])*10 - (time_1+time_2)*10 - (damage1+damage2))
    return f

def fitness_opponents_v1(ind, ports, s1,s2, couple):
    for i,k in enumerate(params.keys()):
        params[k]=ind[i] # recupero valori dei parametri usando l'individuo ind

    # creo 2 clients sui due circuiti avviati
    with Pool(2) as p:
        results=p.starmap(race, [(ports[0],params),(ports[1],params)])
        distRaced_1,time_1,length_1,pos1,damage1,_ = results[0]
        distRaced_2,time_2,length_2,pos2,damage2,_ = results[1]
        del results

    # tempo=0 vuol dire c'e stato un errore
    if time_1==0 or time_2==0: # or distRaced_1<length_1 or distRaced_2<length_2:
        f=math.inf

        # riavvio servers
        s1.stop(True)
        s2.stop()
        
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()
    else:
        # calcolo fitness
        f = -((f1_scores[int(pos1)-1]+f1_scores[int(pos2)-1])*10 + (distRaced_1/time_1+distRaced_2/time_2)*10 - (damage1+damage2))
    return f