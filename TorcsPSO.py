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
warnings.filterwarnings("ignore")
from recover_params import recover_params

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

def fitness(X):
    n=X.shape[0]
    f_results=[]
    for i in range(n):
        x=X[i]
        params = dict(zip(params_keys, x))

        with Pool(2) as p:
            results=p.starmap(race, [(3001,params),(3002,params)])
            #print("results here",results)
            #risultati per il circuito Forza
            distRaced_forza,time_forza,length_forza,check_pos_forza = results[0]
            penalty_forza = (distRaced_forza-length_forza) / 10
            #Risultati per il circuito Wheel1
            distRaced_wheel,time_wheel,length_wheel,check_pos_wheel = results[1]
            penalty_wheel = (distRaced_wheel - length_wheel) / 10
            #Penalità
            penalty = penalty_wheel*penalty_forza
            del results
                
        #Calcolo posizione centrale del veicolo, parametro "trackPos"
        cnt_forza = 0
        cnt_wheel = 0

        for pos in check_pos_forza:
            if pos > 0.7 or pos < -0.7:
                cnt_forza +=1

        for pos in check_pos_wheel:
            if pos > 0.7 or pos < -0.7:
                cnt_wheel +=1
        
        if len(check_pos_forza) != 0:
            check_pos_forza_percentage = cnt_forza/len(check_pos_forza)
        else:
            check_pos_forza_percentage = 0
        
        if len(check_pos_wheel) != 0:
            check_pos_wheel_percentage = cnt_wheel/len(check_pos_wheel)
        else:
            check_pos_wheel_percentage = 0

        if (check_pos_forza_percentage == 0) and (check_pos_wheel_percentage == 0):
            check_pos_final = 0
        else:
            check_pos_final = (check_pos_forza_percentage+check_pos_wheel_percentage)/2

        #print("valutata una fitness")
        #Nel caso in cui la macchina non finisce un giro
        if time_forza == 0 or time_wheel==0:
            f_results.insert(0, math.inf)
        else:
            f=-(-penalty+((distRaced_forza / time_forza) * (distRaced_wheel/time_wheel))-check_pos_final)
            f_results.insert(0, f)
        tqdm.update(2)
    
    # save stats per gen
    #stats["best"].append(-min(f_results))
    stats["avg"].append(np.average([-1*f for f in f_results]))
    stats["stddev"].append(np.std([-1*f for f in f_results]))
    
    return f_results


if __name__ == "__main__":
    # start servers
    server_forza = Server('forza')
    server_forza.setDaemon(True)
    server_forza.start()
    server_wheel = Server('wheel1')
    server_wheel.setDaemon(True)
    server_wheel.start()
    time.sleep(10)

    # Set-up hyperparameters #
    continue_train=False
    seed = 10
    c1=1.49618
    c2=1.49618
    w=0.7298
    options = {'c1': c1, 'c2': c2, 'w': w}#, 'k': 2, 'p': 2} 
    problem_size = 48
    swarm_size = 96
    iterations = 15

    tqdm.total=2*swarm_size*iterations

    init_pos = None
    dirname = "PSO_{}{}{}{}{}".format(swarm_size,iterations,c1,c2,w)
    path_dir = os.path.join(res_path,dirname)
    if not os.path.exists(path_dir): #training da zero
        os.mkdir(path_dir)
    elif continue_train:
        path=recover_params(path_dir)
        if path!="":
            f=open(os.path.join(res_path,path),"r")
            params=json.load(f)['lastGen']
            f.close()
            init_pos = np.vstack([[c] for c in params])

    np.random.seed(seed)
    optimizer = ps.single.GlobalBestPSO(n_particles=swarm_size, dimensions=problem_size, options=options, bounds=bounds, init_pos=init_pos)
    cost, pos = optimizer.optimize(fitness, iters=iterations, verbose=False)
    print("Best solution found: \nX = %s\nF = %s" % ([-1*p for p in pos], -cost))

    stats["lastGen"]=(optimizer.pos_history[-1]).tolist() #salvo tutti i valori dell'ultima generazione (96,48)
    stats["best"]=(optimizer.cost_history).tolist()

    # save best params
    f=open(os.path.join(param_path,"trained_params_{}_gen_PSO".format(iterations)),"w")
    json.dump(dict(zip(params_keys, pos)),f)
    f.close()

    f=open(os.path.join(res_path,"logs_{}_gen_PSO".format(iterations)),"w")
    json.dump(stats,f)
    f.close()

    # # recover history
    # best = stats["best"]
    # avgs = stats["avg"]
    # stddevs = stats["stddev"]

    # # plot convergence
    # plt.title("Convergence")
    # plt.plot(list(range(1,iterations+1,1)), best)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness")
    # plt.yscale("log")
    # plt.xlim((1,iterations))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_convergence_PSO.png".format(iterations)))

    # plt.clf()

    # # plot avg per gen
    # plt.title("Fitness avg per gen")
    # plt.plot(list(range(1,iterations+1,1)), avgs)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness avg")
    # plt.yscale("log")
    # plt.xlim((1,iterations))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_avg_PSO.png".format(iterations)))

    # plt.clf()

    # # plot stddev per gen
    # plt.title("Fitness stddev per gen")
    # plt.plot(list(range(1,iterations+1,1)), stddevs)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness stddev")
    # plt.yscale("log")
    # plt.xlim((1,iterations))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_stddev_PSO.png".format(iterations)))

    exit()