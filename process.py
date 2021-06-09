import csv
import os
import json
from Server import Server
import time
import random
from fitness_func import fitness_opponents
from tqdm import tqdm

# funzione per leggere i files arrivati sul CSV sul Drive; dopo la lattura rimuoviamo il file
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

# funzione per scegliere la sequenza di circuiti per ogni generazione, facendo sì che ogni copppia
# sia usata il 25% di max_gen e due coppie uguali non possono essere generate in due generazioni successive
def choose_circuits(seed, max_gen):
    couples_per_gen = []

    gen=1

    couples = ['1','2','3','4']
    cnt_couples = {'1':0, '2':0, '3':0, '4':0}
    last_couple = ""
    limit = max_gen/len(couples)

    random.seed(seed)

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

if __name__ == "__main__":
    gen=1

    seed=300797 # deve essere uguale a quello settato dal master
    max_gen=20

    # strutture di appoggio
    map_couples = {'1':["forza","wheel1"], '2':["forza","etrack"], '3':["gtrack","wheel1"], '4':["gtrack","etrack"]}
    map_ports = {'1':[3001,3002], '2':[3001,3004], '3':[3003,3002], '4':[3003,3004]}

    # scelta coppie
    circ_per_gen = choose_circuits(seed,max_gen)

    while True:
        solutions=[]
        # recupero coppia da usare in questa generazione
        couple = map_couples[circ_per_gen[gen-1]]
        ports = map_ports[circ_per_gen[gen-1]]

        # faccio partire i servers corrispondenti
        s1 = Server(couple[0])
        s1.setDaemon(True)
        s1.start()
        s2 = Server(couple[1])
        s2.setDaemon(True)
        s2.start()

        # path utili al Drive
        filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
        filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")

        # attesa arrivo file
        while not os.path.exists(filepath_in):
            pass
        
        print("File here - gen: ",gen)

        # lettura file
        individuals = read_file(filepath_in)
        
        # calcolo fitness
        with tqdm(total=len(individuals)) as pbar:
            for ind in individuals:
                solution = fitness_opponents(ind, ports, s1, s2, couple)
                solutions.append(solution)
                pbar.update(1)

        # scrittura risultati su CSV
        print(len(solutions)," calculated")
        csvfile_out = open(filepath_out,"w",newline='')
        spamwriter = csv.writer(csvfile_out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for s in solutions:
            spamwriter.writerow([s])
        print("Finished - gen: ",gen)
        csvfile_out.close()
        gen+=1
        s1.stop(True)
        s2.stop()
    exit()