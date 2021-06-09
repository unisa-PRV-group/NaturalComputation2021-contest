from multiprocessing.pool import Pool
from client import race
import math
from Server import Server
import os
import json

# path utili
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")

# recupero nome parametri
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
params={k:-1 for k in lb.keys()}

def fitness_opponents(ind, ports, s1,s2, couple):
    for i,k in enumerate(params.keys()):
        params[k]=ind[i] # recupero valori dei parametri usando l'individuo ind

    # creo 2 clients sui due circuiti avviati
    with Pool(2) as p:
        results=p.starmap(race, [(ports[0],params),(ports[1],params)])
        distRaced_1,time_1,length_1,pos1,damage1 = results[0]
        distRaced_2,time_2,length_2,pos2,damage2 = results[1]
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
        pos_total = pos1*pos2
        penalty = (penalty_1*penalty_2*pos_total)/10000

        f=-(-penalty + 2*((distRaced_1/time_1)*(distRaced_2/time_1)))
    return f

def fitness_single_circuit(ind,p,s1,c):
    params_d = dict(zip(params, ind))
    distRaced, tot_time, length, pos, damage=race(p,params_d)
    if tot_time==0:
        f=math.inf

        # riavvio servers
        s1.stop(True)
        
        s1 = Server(c)
        s1.setDaemon(True)
        s1.start()
    else:
        # calcolo fitness
        penalty = (distRaced-length)/10000
        f=-(-penalty + 2*((distRaced/tot_time)))

    return f
