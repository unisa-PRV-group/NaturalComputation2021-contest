import numpy as np
from Server import Server
import time
from multiprocessing.pool import Pool
from client import race
import math
import json
import os
import tqdm
import random
from fitness_func import fitness_opponents

from pymoo.model.problem import Problem
from pymoo.algorithms.so_de import DE
from pymoo.optimize import minimize
from pymoo.factory import get_termination
from pymoo.operators.sampling.latin_hypercube_sampling import LatinHypercubeSampling
from pymoo.model.callback import Callback

class CustomCallback(Callback):
    def __init__(self, n_gen, path_res, path_param, keys) -> None:
        super().__init__()
        self.data["best"] = []
        self.data["avg"] = []
        self.data["stddev"] = []
        self.data["lastGen"] = []
        self.cnt_gen=0
        self.max_gen=n_gen
        self.last_save = 0
        self.path_res=path_res
        self.path_param=path_param
        self.param_keys=keys

    def notify(self, algorithm): #chiamata ad ogni generazione
        f_array = algorithm.pop.get("F") # vettore di fitness
        m=f_array.min() #fitness individuo migliore
        avg=np.average(-f_array) #fitness media della popolazione
        std=np.std(-f_array) # deviazione standard della fitness della popolazione

        # salviamo nella struttura di appoggio
        self.data["best"].append(-m)
        self.data["avg"].append(avg)
        self.data["stddev"].append(std)

        print("Fitness -> Best: {} - Avg: {} - Stddev: {}".format(-m, avg, std))

        self.cnt_gen+=1
        self.last_save+=1
        if self.last_save==1: # ogni generazione viene scritto il file dei risultati
            self.data["lastGen"]=algorithm.pop.get("X").tolist() # tutta la popolazione di questa generazione
            # trovo individuo migliore
            index=np.where(f_array==m)[0][0]
            best_ind = self.data["lastGen"][index]
            
            # salvo i risultati
            f=open(os.path.join(path_dir_p,"trained_params_{}_gen_7".format(self.cnt_gen)),"w")
            json.dump(dict(zip(self.param_keys, best_ind)),f)
            f.close()

            f=open(os.path.join(path_dir,"logs_{}_gen_7".format(self.cnt_gen)),"w")
            json.dump(self.data,f)
            f.close()

            self.last_save=0

# classe per definire il problema da ottimizzare
class RaceProblem(Problem):
    def __init__(self, path, n_pop, max_gens):
        # definisco i bound per i parametri
        f=open(os.path.join(path,"lower_bounds"), 'r')
        lb = json.load(f)
        f.close()
        f=open(os.path.join(path,"upper_bounds"), 'r')
        ub = json.load(f)
        f.close()

        self.params_keys = list(lb.keys())
        self.lower_bounds=[value for value in lb.values()]
        self.upper_bounds=[value for value in ub.values()]

        self.map_couples = {'1':["forza","wheel1"], '2':["forza","etrack"], '3':["gtrack","wheel1"], '4':["gtrack","etrack"]}
        self.ports = {'1':[3001,3002], '2':[3001,3004], '3':[3003,3002], '4':[3003,3004]}

        self.cnt_gen = 0 # generazione corrente
        self.max_gen = max_gens #massimo numero di generazioni
        self.tqdm=tqdm.tqdm(total=n_pop*max_gens)
        super().__init__(n_var=len(self.params_keys), n_obj=1, n_constr=0, xl=self.lower_bounds, xu=self.upper_bounds, elementwise_evaluation=False)

    def choose_circuits(self, max_gen):
        couples_per_gen = []

        gen=1

        couples = ['1','2','3','4']
        cnt_couples = {'1':0, '2':0, '3':0, '4':0}
        last_couple = ""
        limit = max_gen/len(couples)

        while gen<=max_gen:
            while True:
                if len(couples)>1:
                    r=random.choice(couples)
                    if r!=last_couple:
                        last_couple=r
                        cnt_couples[r]+=1
                        if cnt_couples[r]==limit:
                            couples.remove(r)
                        couples_per_gen.append(last_couple)
                        break
                else: 
                    r=couples[0]
                    cnt_couples[r]+=1
                    couples_per_gen.append(r)
                    if cnt_couples[r]==limit:
                        couples.remove(r)
                    break
            gen+=1
        return couples_per_gen

    def _evaluate(self, X, out, *args, **kwargs):
        self.cnt_gen+=1
        solutions=[]

        # SCEGLIAMO I DUE CIRCUITI #
        circ_per_gen = self.choose_circuits(self.max_gen)
        couple = self.map_couples[circ_per_gen[self.cnt_gen-1]]

        # FACCIAMO PARTIRE I SERVERS #
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()

        n=X.shape[0] # numero di individui nella popolazione
        for i in range(n):
            x=X[i]
            sol = fitness_opponents(x, self.ports[circ_per_gen[self.cnt_gen-1]],s1,s2,couple)
            solutions.append(sol)
            self.tqdm.update(1)

        out["F"] = np.array(solutions, dtype='float')

if __name__ == "__main__":
    # population size
    n_pop = 240
    # number of variables for the problem visualization
    n_vars = 48
    # maximum number of generations
    max_gens = 20
    
    ## PARAMETERS ##
    CR=0.75
    F=0.9
    seed=300797

    ## DEFINIZIONE DI PATHS ##
    base_path=os.path.realpath(os.path.dirname(__file__))
    param_path=os.path.join(base_path,"parameters")
    res_path=os.path.join(base_path,"results")
    
    # convenzione: algoritmo_{popsize}{maxgen}{CR}{F}{seed}
    dirname="DE_240100.60.810" # cartella in cui salvare i risultati
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
        f=open(os.path.join(path_dir,filepath),"r")
        params=json.load(f)['lastGen']
        f.close()
        sampling = np.vstack([[c] for c in params])
    else: sampling = LatinHypercubeSampling(iterations=100, criterion="maxmin")

    ## PROBLEM DEFINITION ##
    problem=RaceProblem(param_path, n_pop, max_gens)
    termination = get_termination("n_gen", max_gens)
    callback=CustomCallback(max_gens, path_dir, path_dir_p, problem.params_keys)
    algorithm = DE(pop_size=n_pop, sampling=sampling,
                   variant="DE/rand/1/bin", CR=CR, F=F, dither="vector", jitter=True,
                   eliminate_duplicates=True)
    res = minimize(problem, algorithm, termination, callback=callback, seed=seed, verbose=False, save_history=False)
    
    ## SALVATAGGIO RISULTATI ULTIMA GENERAZIONE ##
    f=open(os.path.join(path_dir_p,"trained_params_{}_gen_7".format(max_gens)),"w")
    json.dump(dict(zip(problem.params_keys, res.X)),f)
    f.close()

    f=open(os.path.join(path_dir,"logs_{}_gen_7".format(max_gens)),"w")
    json.dump(res.algorithm.callback.data,f)
    f.close()

    print("Best solution found: \nX = %s\nF = %s" % (res.X, -res.F))
    
    exit()

# DURATA: 15 ORE CIRCA
