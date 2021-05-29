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

# recover params name
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
f=open(os.path.join(param_path,"lower_bounds"), 'r')
lb = json.load(f)
f.close()
params={k:-1 for k in lb.keys()}

# n_pop=100
# bar = tqdm(total=n_pop, disable=True)

filepath_out=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\output_1.csv")
filepath_in=os.path.abspath("F:\\Drive condivisi\\NaturalComputation_FinalContest2021\\input_1.csv")

if __name__ == "__main__":
    server_forza = Server('forza')
    server_forza.setDaemon(True)
    server_forza.start()
    server_wheel = Server('wheel1')
    server_wheel.setDaemon(True)
    server_wheel.start()
    time.sleep(10)

    csvfile_in = open(filepath_in,"r",newline='')
    csv_reader = csv.reader(csvfile_in, delimiter=',')

    solutions=[]

    while True:
        # bar.disable=False
        # if bar.n!=0: bar.reset()

        while not os.path.exists(filepath_in):
            pass
        
        print("File here")
            
        for row in csv_reader: # for each individual, aka 48 params
            if len(row)!=0:
                for i,k in enumerate(params.keys()):
                    params[k]=float(row[i])

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
                    f=math.inf
                else:
                    f=-(-penalty+((distRaced_forza / time_forza) * (distRaced_wheel/time_wheel))-check_pos_final)
                
                print(f)

                solutions.append(str(f))

        # write results
        csvfile_out = open(filepath_out,"a",newline='')
        spamwriter = csv.writer(csvfile_out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(solutions)
        print("Finished")

                # tqdm.update(2)