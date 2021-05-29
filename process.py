import csv
from multiprocessing.pool import Pool
from client import race
import math
import os
import json
from tqdm import tqdm

# recover params name
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
params={k:-1 for k in lb.keys()}

n_pop=100
bar = tqdm(total=n_pop)

filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")

while(True):

    while not os.path.exists(filepath_in):
        pass

    with open(filepath_in,"r",newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader: # for each individual, aka 48 params
            if len(row)!=0:
                for i,k in enumerate(params.keys()):
                    params[k]=row[i]

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
                f=[math.inf]
            else:
                f=-(-penalty+((distRaced_forza / time_forza) * (distRaced_wheel/time_wheel))-check_pos_final)

            # write results
            with open(filepath_out,"a",newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quotechar='""', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow(f)

            tqdm.update(2)