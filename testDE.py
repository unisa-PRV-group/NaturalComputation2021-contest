import json
import os
from Server import Server
from client import race
import matplotlib.pyplot as plt
import time
from multiprocessing.pool import Pool

f_without_opp = "trained_params_32_gen_3"
f_opp = "trained_params_20_gen_7"

base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")

def graphic_simulation():
    f=open(os.path.join(param_path,"DE_240100.60.810_opp/{}".format(f_without_opp)),"r")
    race(3001,dict(json.load(f)),test=True)
    f.close()

def quick_simulation_with_speed_profile():
    circuit1 = 'cgtrack2'
    circuit2 = 'etrack3'
    server_1 = Server(circuit1)
    server_1.setDaemon(True)
    server_1.start()
    server_2 = Server(circuit2)
    server_2.setDaemon(True)
    server_2.start()
    time.sleep(10)

    # default
    with Pool(2) as p:
        f=open(os.path.join(param_path,"default_parameters"),"r")
        params = dict(json.load(f))
        f.close()
        results_def=p.starmap(race, [(3001,params,True),(3002,params,True)])
        #speeds_def, times_def, first_lap_def = race(3001,dict(json.load(f)),test=True)
        print("Default race finished")
        p.close()

    # nostro
    with Pool(2) as p:
        f=open(os.path.join(param_path,"DE_96150.60.810/trained_params_32_gen_3"),"r")
        params=dict(json.load(f))
        f.close()
        results_trained=p.starmap(race, [(3001,params,True),(3002,params,True)])
        #speeds, times, first_lap = race(3001,dict(json.load(f)),test=True)
        print("Trained race finished")
        p.close()

    plt.figure(1)
    plt.title("Speed profile {}".format(circuit1))
    plt.plot(results_trained[0][1], [s for s in results_trained[0][0]], color="blue")
    plt.plot(results_def[0][1], [s for s in results_def[0][0]], color="orange")
    plt.legend(["Trained", "Default"])
    plt.ylabel("Speed (km/h)")
    plt.xlabel("Time (s)")
    plt.axvline(x=results_trained[0][2], linestyle="dashed", color="blue")
    plt.axvline(x=results_def[0][2], linestyle="dashed", color="orange")

    plt.figure(2)
    plt.title("Speed profile {}".format(circuit2))
    plt.plot(results_trained[1][1], [s for s in results_trained[1][0]], color="blue")
    plt.plot(results_def[1][1], [s for s in results_def[1][0]], color="orange")
    plt.legend(["Trained", "Default"])
    plt.ylabel("Speed (km/h)")
    plt.xlabel("Time (s)")
    plt.axvline(x=results_trained[1][2], linestyle="dashed", color="blue")
    plt.axvline(x=results_def[1][2], linestyle="dashed", color="orange")
    plt.show()

    server_1.stop(True)
    server_2.stop()

    exit()

if __name__ == "__main__":
    graphic_simulation()