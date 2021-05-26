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

from pymoo.model.problem import Problem
from pymoo.algorithms.so_de import DE
from pymoo.optimize import minimize
from pymoo.factory import get_problem, get_visualization, get_termination
from pymoo.operators.sampling.latin_hypercube_sampling import LatinHypercubeSampling

class RaceProblem(Problem):
    #xl=[63.7655, 1.4188, 1.0383, 2.0183, 2.0627, 33.8688, 81.3069, 45.2619, 0.0100, 3411.4781, 5366.0837, 5965.5188, 6315.7639, 6360.9504, 0.7379, 18.06372, 10.7936, 1.2082, 90.5418, 1.0003, 0.0659, 2.1964, 0.4602, 2.5537, 0.0013, 25.1222, 0.4613, 0.0090, 1.2033, 0.1025, 1.7450, 0.0514, 551.9643, 263.3230, 0.8552, 0.1438, 395.5263, 16.0833, 0.2760, 0.5786, 0.9002, 8099.1962, 8091.3063, 8097.7155, 8204.8691, 8935.8770, 0.6843, 3.8140],
    #xu=[77.9356, 1.9195, 1.1421, 2.2426, 2.9794, 38.9491, 99.3751, 55.3201, 0.02, 4615.5291 , 7259.9955,  8070.9960, 8544.8571, 8605.9918 , 0.90189, 22.07788, 21.5872, 1.5438, 104.8379, 1.0003, 0.0659, 2.1964, 0.5624, 3.4551, 0.0026, 30.7048, 0.6919, 0.0180, 1.5041, 0.1025, 1.7450, 0.0514, 827.9465, 394.9844, 1.0452, 0.1726, 593.2895, 24.1250, 0.5520, 0.7072, 1.1002, 10957.7360, 10947.0615, 10955.7327, 11100.7053, 10127.3273, 1.0265, 4.4870])
    def __init__(self):
        # definisco i bound per i parametri
        path=os.path.join(os.path.realpath(os.path.dirname(__file__)),"parameters")
        print(path)
        lb = json.load(open(os.path.join(path,"lower_bounds"), 'r'))
        ub = json.load(open(os.path.join(path,"upper_bounds"), 'r'))
        self.params_keys = list(lb.keys())
        self.lower_bounds=[value for value in lb.values()]
        self.upper_bounds=[value for value in ub.values()]
        self.tqdm=tqdm.tqdm(total=200)
        #print(len(self.params_keys), len(self.lower_bounds), len(self.upper_bounds))
        super().__init__(n_var=48, n_obj=1, n_constr=0, xl=self.lower_bounds, xu=self.upper_bounds, elementwise_evaluation=True)

    def _evaluate(self, X, out, *args, **kwargs):
        #ricostruisco il dizionario dei parametri
        params = dict(zip(self.params_keys, X))
        with Pool(2) as p:
            results=p.starmap(race, [(3001,params),(3002,params)])
            #print("results here",results)
            #risultati per il circuito Forza
            distRaced_forza,time_forza,length_forza = results[0]
            penalty_forza = (distRaced_forza-length_forza) / 10
            #Risultati per il circuito Wheel1
            distRaced_wheel,time_wheel,length_wheel = results[1]
            penalty_wheel = (distRaced_wheel - length_wheel) / 10
            #Penalità
            penalty = penalty_wheel*penalty_forza
            del results
        #print("valutata una fitness")
        #Nel caso in cui la macchina non finisce un giro
        if time_forza == 0 or time_wheel==0:
            f=math.inf
        f=-(-penalty+((distRaced_forza / time_forza) * (distRaced_wheel/time_wheel)))
        out["F"] = np.array(f, dtype='float')
        self.tqdm.update(2)

if __name__ == "__main__":
    # population size
    n_pop = 100
    # number of variables for the problem visualization
    n_vars = 48
    # maximum number of generations
    max_gens = 10

    # start servers
    server_forza = Server('forza')
    server_forza.start()
    server_wheel = Server('wheel1')
    server_wheel.start()
    time.sleep(10)

    # get problem
    problem=RaceProblem()

    termination = get_termination("n_gen", max_gens)

    algorithm = DE(pop_size=n_pop, sampling=LatinHypercubeSampling(iterations=100, criterion="maxmin"),
                   variant="DE/rand/1/bin", CR=0.7, F=0.3, dither="vector", jitter=True,
                   eliminate_duplicates=True)
                   
    res = minimize(problem, algorithm, termination, seed=1, verbose=False, save_history=True)
    
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))

    # plot convergence
    n_evals = np.array([e.evaluator.n_eval for e in res.history])
    opt = np.array([e.opt[0].F for e in res.history])

    plt.title("Convergence")
    plt.plot(n_evals, opt, "-")
    plt.yscale("log")
    plt.show()
