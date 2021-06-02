import csv
from multiprocessing.pool import Pool
from client import race
import math
import os
import json
from tqdm import tqdm
from client import race
from Server import Server
import time
import random

# recover params name
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
params={k:-1 for k in lb.keys()}

#bar = tqdm(total=84)

def read_file(filename):
    parameters = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
                parameters.append([])
                for value in row:
                    parameters[-1].append(float(value))
    os.remove(filename)
    return parameters

if __name__ == "__main__":
    gen=1

    map_couples = {'1':["forza","wheel1"], '2':["forza","etrack"], '3':["gtrack","wheel1"], '4':["gtrack","etrack"]}
    ports = {'1':[3001,3002], '2':[3001,3004], '3':[3003,3002], '4':[3003,3004]}
    couples = list(map_couples.keys())
    cnt_couples = {'1':0, '2':0, '3':0, '4':0}
    last_couple = ""
    limit = 100/len(couples)

    while True:

        solutions=[]

        # choose servers couple
        while(True):
            r=random.choice(couples) #1,n n=numero circuiti
            if r!=last_couple:
                last_couple=r
                cnt_couples[r]+=1
                if cnt_couples[r]==limit: couples.remove(r)
                break
        couple = map_couples[last_couple]
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()

        filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
        filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")

        while not os.path.exists(filepath_in):
            pass
        
        print("File here - gen: ",gen)

        individuals = read_file(filepath_in)
        
        with tqdm(total=len(individuals)) as pbar:
            for ind in individuals: # for each individual, aka 48 params
                #start = time.time()
                for i,k in enumerate(params.keys()):
                    params[k]=ind[i]

                with Pool(2) as p:
                    results=p.starmap(race, [(ports[last_couple][0],params),(ports[last_couple][1],params)])
                    #print("results here",results)
                    #risultati per il circuito Forza
                    distRaced_1,time_1,length_1,check_pos_1 = results[0]
                    penalty_1 = distRaced_1-length_1
                    #Risultati per il circuito Wheel1
                    distRaced_2,time_2,length_2,check_pos_2 = results[1]
                    penalty_2 = distRaced_2 - length_2
                    #Penalità
                    penalty = (penalty_1*penalty_2 + len(check_pos_1)*len(check_pos_2))/100000
                    del results
            
                if time_1 == 0 or time_2==0:
                    f=math.inf
                else:
                    f=-(-penalty+2*((distRaced_1 / time_1) * (distRaced_2/time_2)))

                solutions.append(f)
                
                pbar.update(1)

        # write results
        print(len(solutions)," calculated")
        csvfile_out = open(filepath_out,"w",newline='')
        spamwriter = csv.writer(csvfile_out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for s in solutions:
            spamwriter.writerow([s])
        print("Finished - gen: ",gen)
        csvfile_out.close()
        gen+=1
        s1.stop()
        s2.stop()
    exit()