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

from custom_pool import CustomPool

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

def evaluate(individuals, index):
    names=[]
    print("thread {} partito".format(index))
    if index==1:
        names=["forza","wheel1"]
        ports=[3001,3002]
    else:
        names=["forza_2","wheel1_2"]
        ports=[3003,3004]

    server_forza = Server(names[0])
    server_forza.setDaemon(True)
    server_forza.start()
    server_wheel = Server(names[1])
    server_wheel.setDaemon(True)
    server_wheel.start()
    #time.sleep(10)

    solutions=[]

    #with tqdm(total=len(individuals)) as pbar:
    for j,ind in enumerate(individuals): # for each individual, aka 48 params
        #start = time.time()
        for i,k in enumerate(params.keys()):
            params[k]=ind[i]

        with Pool(2) as p:
            results=p.starmap(race, [(ports[0],params),(ports[1],params)])
            #print("results here",results)
            #risultati per il circuito Forza
            distRaced_forza,time_forza,length_forza,check_pos_forza = results[0]
            penalty_forza = distRaced_forza-length_forza
            #Risultati per il circuito Wheel1
            distRaced_wheel,time_wheel,length_wheel,check_pos_wheel = results[1]
            penalty_wheel = distRaced_wheel - length_wheel
            #Penalità
            penalty = (penalty_wheel*penalty_forza)/10
            del results

        cnt_forza = len(check_pos_forza)
        cnt_wheel = len(check_pos_wheel)

        # for pos in check_pos_forza:
        #     if pos > 0.5 or pos < -0.5:
        #         cnt_forza +=1

        # for pos in check_pos_wheel:
        #     if pos > 0.5 or pos < -0.5:
        #         cnt_wheel +=1

        check_pos_final = (cnt_forza*cnt_wheel)/10000

        #print("valutata una fitness")
        #Nel caso in cui la macchina non finisce un giro
        if time_forza == 0 or time_wheel==0:
            f=math.inf
        else:
            f=-(-penalty+2*((distRaced_forza / time_forza) * (distRaced_wheel/time_wheel))-check_pos_final)

        solutions.append(f)
        print("Thread",index," -> ",j+1,"/",len(individuals))

    return solutions


if __name__ == "__main__":
    gen=1

    while True:

        solutions=[]

        filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
        filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")

        while not os.path.exists(filepath_in):
            pass
        
        print("File here - gen: ",gen)

        start = time.time()

        individuals = read_file(filepath_in)
        n=len(individuals)

        chunk1=[]
        chunk2=[]
        for i in individuals[:int(n/2)][:]:
            if len(i)!=48: print("Error ",len(i))
            chunk1.append(i)
        for i in individuals[int(n/2):][:]:
            if len(i)!=48: print("Error ",len(i))
            chunk2.append(i)

        p=CustomPool(2)
        partial_solution = p.starmap(evaluate, [(chunk1,1), (chunk2,2)])
        print("Threads done, writing...")
        p.close()
        p.join()

        solutions.extend((partial_solution[0],partial_solution[1]))
        del partial_solution
        
        # write results
        print(len(solutions)," calculated")
        csvfile_out = open(filepath_out,"w",newline='')
        spamwriter = csv.writer(csvfile_out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for s in solutions:
            spamwriter.writerow([s])
        elapsed_time = time.time() - start
        print("Finished - Elapsed time: ",elapsed_time)
        csvfile_out.close()
        gen+=1
    exit()