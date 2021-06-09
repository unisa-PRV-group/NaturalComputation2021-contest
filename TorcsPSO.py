# Import modules
import numpy as np
import matplotlib.pyplot as plt
# Import PySwarms
import pyswarms as ps
from pyswarms.utils.functions import single_obj as fx
from pyswarms.utils.plotters import plot_cost_history
import os
from multiprocessing.pool import Pool
from client import race
import math
import json
import tqdm
from Server import Server
import time
import warnings
import random
warnings.filterwarnings("ignore")
from fitness_func import fitness_single_circuit

# paths
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
fig_path=os.path.join(base_path,"doc")
res_path=os.path.join(base_path,"results")

# values
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
f=open(os.path.join(param_path,"upper_bounds"), 'r')
ub = json.load(f)
f.close()
params_keys = list(lb.keys())
lower_bounds=[value for value in lb.values()]
upper_bounds=[value for value in ub.values()]
bounds=(lower_bounds,upper_bounds)
tqdm=tqdm.tqdm()
stats = {'best':[], 'avg':[], 'stddev':[]}

map_couples = {'1':"1", '2':"2", '3':"3", '4':"4"}
ports = {'1':3001, '2':3002, '3':3003, '4':3004}
cnt_gen = 0

def choose_circuits(seed,max_gen):
    couples_per_gen = []

    gen=1

    couples = ['1','2','3','4']
    cnt_couples = {'1':0, '2':0, '3':0, '4':0}
    last_couple = ""
    limit = max_gen/len(couples)

    random.seed(seed)

    while gen<=max_gen:
        #print("\nGen: {} -> couples: {}; last couple: {}".format(gen, couples, last_couple))
        while True:
            if len(couples)>1:
                r=random.choice(couples) #1,n n=numero circuiti
                #print("Generated couple n.{}".format(r))
                if r!=last_couple:
                    #print("Right couple generated")
                    last_couple=r
                    cnt_couples[r]+=1
                    #print("Current counts: ",cnt_couples)
                    if cnt_couples[r]==limit:
                        couples.remove(r)
                        #print("Couple {} has overcomed limit".format(r))
                    couples_per_gen.append(last_couple)
                    break
                #else: print("Couple already generated")
            else: 
                #print("One element only -> choose it")
                r=couples[0]
                cnt_couples[r]+=1
                couples_per_gen.append(r)
                if cnt_couples[r]==limit:
                    couples.remove(r)
                    #print("Couple {} has overcomed limit".format(r))
                break
        gen+=1
        #time.sleep(1)
    return couples_per_gen

map_couples = {'1':"forza", '2':"wheel1", '3':"gtrack", '4':"etrack"}
circ_per_gen = choose_circuits(11111, 48) #Numero di generazioni
ports = {'1':3001, '2':3002, '3':3003, '4':3004}

def fitness(X,**args):
    global cnt_gen
    cnt_gen += 1
    n=X.shape[0]
    f_results=[]
    for i in range(n):
        x=X[i]
        
        c = map_couples[circ_per_gen[cnt_gen-1]]
        
        #Start Server
        s1 = Server(c)
        s1.setDaemon(True)
        s1.start()

        f = fitness_single_circuit(x,ports[circ_per_gen[cnt_gen-1]],s1,c)

        s1.stop(True)
        tqdm.update(1)
    f_results.append(f)
    
    # save stats per gen
    opt=args["opt"]
    stats["avg"].append(np.average([-1*f for f in f_results]))
    stats["stddev"].append(np.std([-1*f for f in f_results]))
    stats["best"].append(-min(f_results))
    stats["lastGen"]=(opt.pos_history[-1]).tolist() #salvo tutti i valori dell'ultima generazione

    # save best params
    path_dir_p=args["path_res"]
    f=open(os.path.join(path_dir_p,"trained_params_{}_gen".format(iterations)),"w")
    json.dump(dict(zip(params_keys, pos)),f)
    f.close()

    path_dir=args["path_logs"]
    f=open(os.path.join(path_dir,"logs_{}_gen".format(iterations)),"w")
    json.dump(stats,f)
    f.close()
    
    s1.stop(True)

    return f_results

if __name__ == "__main__":

    # Set-up hyperparameters #
    continue_train=False
    seed = 11111
    c1=1.49618
    c2=1.49618
    w=0.7298
    options = {'c1': c1, 'c2': c2, 'w': w}#, 'k': 2, 'p': 2} 
    problem_size = 48
    swarm_size = 144
    iterations = 48

    tqdm.total=swarm_size*iterations

    ## DEFINIZIONE DI PATHS ##
    base_path=os.path.realpath(os.path.dirname(__file__))
    param_path=os.path.join(base_path,"parameters")
    res_path=os.path.join(base_path,"results")

    # convenzione: algoritmo_{popsize}{maxgen}{c1}{c2}{w}{seed}
    dirname="PSO_240100.60.810" # cartella in cui salvare i risultati
    path_dir = os.path.join(res_path,dirname)
    path_dir_p = os.path.join(param_path, dirname)
    if not os.path.exists(path_dir_p):
        os.mkdir(path_dir_p)
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)

    # MODIFICARE QUESTO FLAG PER FAR PARTIRE IL TRAINING DA UNO VECCHIO
    continue_train = False

    if continue_train:
        filepath = "logs_20_gen_7" # file da cui recuperare la generazione di partenza
        f=open(os.path.join(res_path,filepath),"r")
        params=json.load(f)['lastGen']
        f.close()
        init_pos = np.vstack([[c] for c in params])
    else: init_pos=None

    ## PROBLEM DEFINITION ##
    np.random.seed(seed)
    optimizer = ps.single.GlobalBestPSO(n_particles=swarm_size, dimensions=problem_size, options=options, bounds=bounds, init_pos=init_pos)
    args={"opt":None, "path_logs":path_dir, "path_res":path_dir_p}
    cost, pos = optimizer.optimize(fitness, iters=iterations, verbose=False, kwargs=args)
    print("Best solution found: \nX = %s\nF = %s" % ([-1*p for p in pos], -cost))

    exit()

# TEMPO STIMATO: 41 ore