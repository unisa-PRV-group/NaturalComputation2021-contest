import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from Server import Server
import time
from multiprocessing.pool import Pool
from client import race
import math
import json
import os
import tqdm
from recover_params import recover_params
import csv

from pymoo.model.problem import Problem
from pymoo.algorithms.so_de import DE
from pymoo.optimize import minimize
from pymoo.factory import get_problem, get_visualization, get_termination
from pymoo.operators.sampling.latin_hypercube_sampling import LatinHypercubeSampling
from pymoo.model.callback import Callback

class CustomCallback(Callback):
    def __init__(self, n_gen) -> None:
        super().__init__()
        self.data["best"] = []
        self.data["avg"] = []
        self.data["stddev"] = []
        self.data["lastGen"] = []
        self.cnt=n_gen

    def notify(self, algorithm):
        f_array = -algorithm.pop.get("F")
        self.data["best"].append(f_array.min())
        self.data["avg"].append(np.average(f_array))
        self.data["stddev"].append(np.std(f_array))
        self.cnt-=1
        if self.cnt==0:
            self.data["lastGen"]=algorithm.pop.get("X").tolist()

class RaceProblem(Problem):
    #xl=[63.7655, 1.4188, 1.0383, 2.0183, 2.0627, 33.8688, 81.3069, 45.2619, 0.0100, 3411.4781, 5366.0837, 5965.5188, 6315.7639, 6360.9504, 0.7379, 18.06372, 10.7936, 1.2082, 90.5418, 1.0003, 0.0659, 2.1964, 0.4602, 2.5537, 0.0013, 25.1222, 0.4613, 0.0090, 1.2033, 0.1025, 1.7450, 0.0514, 551.9643, 263.3230, 0.8552, 0.1438, 395.5263, 16.0833, 0.2760, 0.5786, 0.9002, 8099.1962, 8091.3063, 8097.7155, 8204.8691, 8935.8770, 0.6843, 3.8140],
    #xu=[77.9356, 1.9195, 1.1421, 2.2426, 2.9794, 38.9491, 99.3751, 55.3201, 0.02, 4615.5291 , 7259.9955,  8070.9960, 8544.8571, 8605.9918 , 0.90189, 22.07788, 21.5872, 1.5438, 104.8379, 1.0003, 0.0659, 2.1964, 0.5624, 3.4551, 0.0026, 30.7048, 0.6919, 0.0180, 1.5041, 0.1025, 1.7450, 0.0514, 827.9465, 394.9844, 1.0452, 0.1726, 593.2895, 24.1250, 0.5520, 0.7072, 1.1002, 10957.7360, 10947.0615, 10955.7327, 11100.7053, 10127.3273, 1.0265, 4.4870])
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
        self.tqdm=tqdm.tqdm(total=max_gens)
        #print(len(self.params_keys), len(self.lower_bounds), len(self.upper_bounds))
        super().__init__(n_var=len(self.params_keys), n_obj=1, n_constr=0, xl=self.lower_bounds, xu=self.upper_bounds, elementwise_evaluation=False)

    def _evaluate(self, X, out, *args, **kwargs): # X -> (n_pop,48)
        filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")
        filepath_in2=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_2.csv")

        n=X.shape[0]

        #45% -> 108 -> 0,107 S
        #35% -> 84 -> 108,191 c1
        # 48 -> 192,239 c2

        # write input files
        with open(filepath_in,"w",newline='') as csvfile:
            for i in range(108,192):
                x=X[i]
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(x)

        with open(filepath_in2,"w",newline='') as csvfile:
            for i in range(192,n):
                x=X[i]
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(x)

        # read outputs
        filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
        filepath_out2=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_2.csv")

        solutions = []

        for i in range(108):
            x=X[i]
            params=dict(zip(self.params_keys,x))
            with Pool(2) as p:
                results=p.starmap(race, [(3001,params),(3002,params)])
                #print("results here",results)
                #risultati per il circuito Forza
                distRaced_forza,time_forza,length_forza,check_pos_forza = results[0]
                penalty_forza = distRaced_forza-length_forza
                #Risultati per il circuito Wheel1
                distRaced_wheel,time_wheel,length_wheel,check_pos_wheel = results[1]
                penalty_wheel = distRaced_wheel - length_wheel
                #Penalità
                penalty = (penalty_wheel+penalty_forza)/2
                del results
                p.close()
        
            if time_forza == 0 or time_wheel==0:
                f=[math.inf]
            else:
                #Calcolo posizione centrale del veicolo, parametro "trackPos"
                cnt_forza = 0
                cnt_wheel = 0

                lf = len(check_pos_forza)
                lw = len(check_pos_wheel)        
                
                if lf != 0:
                    for pos in check_pos_forza:
                        if pos > 0.7 or pos < -0.7:
                            cnt_forza +=1
                    check_pos_forza_percentage = cnt_forza/lf
                else:
                    check_pos_forza_percentage = 0
                
                if lw != 0:
                    for pos in check_pos_wheel:
                        if pos > 0.7 or pos < -0.7:
                            cnt_wheel +=1
                    check_pos_wheel_percentage = cnt_wheel/lw
                else:
                    check_pos_wheel_percentage = 0

                if (check_pos_forza_percentage == 0) and (check_pos_wheel_percentage == 0):
                    check_pos_final = 0
                else:
                    check_pos_final = (check_pos_forza_percentage+check_pos_wheel_percentage)/2
        
                f=-(-0.1*penalty+0.6*((distRaced_forza / time_forza) + (distRaced_wheel/time_wheel))/2-0.3*check_pos_final)

            solutions.append(str(f))

        while not os.path.exists(filepath_out) and not os.path.exists(filepath_out2):
            pass

        with open(filepath_out,"r",newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader: # each result
                if len(row)!=0:
                    solutions.append(float(row))

        with open(filepath_out2,"r",newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader: # each result
                if len(row)!=0:
                    solutions.append(float(row))

        out["F"] = np.array(solutions, dtype='float')
        self.tqdm.update(1)

if __name__ == "__main__":
    # population size
    n_pop = 240
    # number of variables for the problem visualization
    n_vars = 48
    # maximum number of generations
    max_gens = 10

    CR=0.7
    F=0.9
    seed=1

    continue_train = False

    # start servers
    # server_forza = Server('forza')
    # server_forza.setDaemon(True)
    # server_forza.start()
    # server_wheel = Server('wheel1')
    # server_wheel.setDaemon(True)
    # server_wheel.start()
    # time.sleep(10)

    # definition of useful paths
    base_path=os.path.realpath(os.path.dirname(__file__))
    param_path=os.path.join(base_path,"parameters")
    fig_path=os.path.join(base_path,"doc")
    res_path=os.path.join(base_path,"results")
    
    sampling = LatinHypercubeSampling(iterations=100, criterion="maxmin")

    # recover params
    dirname = "DE_{}{}{}{}{}".format(n_pop,max_gens,CR,F,seed)
    path_dir = os.path.join(res_path,dirname)
    if not os.path.exists(path_dir): #training da zero
        os.mkdir(path_dir)
    elif continue_train:
        path=recover_params(path_dir)
        if path!="":
            f=open(os.path.join(res_path,path),"r")
            params=json.load(f)['lastGen']
            f.close()
            sampling = np.vstack([[c] for c in params])

    # get problem
    problem=RaceProblem(param_path, n_pop, max_gens)

    termination = get_termination("n_gen", max_gens)
    callback=CustomCallback(n_gen=max_gens)

    algorithm = DE(pop_size=n_pop, sampling=sampling,
                   variant="DE/rand/1/bin", CR=CR, F=F, dither="vector", jitter=True,
                   eliminate_duplicates=True)
                   
    res = minimize(problem, algorithm, termination, callback=callback, seed=seed, verbose=False, save_history=False)
    
    # save best params
    path_dir_p = os.path.join(param_path, dirname)
    if not os.path.exists(path_dir_p): #training da zero
        os.mkdir(path_dir_p)
    f=open(os.path.join(path_dir_p,"trained_params_{}_gen".format(max_gens)),"w")
    json.dump(dict(zip(problem.params_keys, res.X)),f)
    f.close()

    f=open(os.path.join(path_dir,"logs_{}_gen".format(max_gens)),"w")
    json.dump(res.algorithm.callback.data,f)
    f.close()

    print("Best solution found: \nX = %s\nF = %s" % (res.X, -res.F))

    # recover history
    # best = res.algorithm.callback.data["best"]
    # avgs = res.algorithm.callback.data["avg"]
    # stddevs = res.algorithm.callback.data["stddev"]

    # # plot convergence
    # plt.title("Convergence")
    # plt.plot(list(range(1,max_gens+1,1)), best)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness")
    # plt.yscale("log")
    # plt.xlim((1,max_gens))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_convergence.png".format(max_gens)))

    # plt.clf()

    # # plot avg per gen
    # plt.title("Fitness avg per gen")
    # plt.plot(list(range(1,max_gens+1,1)), avgs)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness avg")
    # plt.yscale("log")
    # plt.xlim((1,max_gens))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_avg.png".format(max_gens)))

    # plt.clf()

    # # plot stddev per gen
    # plt.title("Fitness stddev per gen")
    # plt.plot(list(range(1,max_gens+1,1)), stddevs)
    # plt.xlabel("Generation")
    # plt.ylabel("Fitness stddev")
    # plt.yscale("log")
    # plt.xlim((1,max_gens))
    # #plt.show()
    # plt.savefig(os.path.join(fig_path,"{}_gen_stddev.png".format(max_gens)))
    
    exit()