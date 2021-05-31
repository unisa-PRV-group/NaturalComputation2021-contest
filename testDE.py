import json
import os
from Server import Server
from client import race
import matplotlib.pyplot as plt
import time
from multiprocessing.pool import Pool

def graphic_simulation():
    base_path=os.path.realpath(os.path.dirname(__file__))
    param_path=os.path.join(base_path,"parameters")
    
    f=open(os.path.join(param_path,"default_parameters"),"r")
    speeds_def, times_def, first_lap_def = race(3001,dict(json.load(f)),test=True)
    print("Default race finished")
    f.close()

    f=open(os.path.join(param_path,"DE_96150.60.810/trained_params_15_gen"),"r")
    speeds, times, first_lap = race(3001,dict(json.load(f)),test=True)
    f.close()
    print("Trained race finished")

    plt.figure()
    plt.title("Speed profile")
    plt.plot(times, [s for s in speeds], color="blue")
    plt.plot(times_def, [s for s in speeds_def], color="orange")
    plt.legend(["Trained", "Default"])
    plt.ylabel("Speed (km/h)")
    plt.xlabel("Time (s)")
    plt.axvline(x=first_lap, linestyle="dashed", color="blue")
    plt.axvline(x=first_lap_def, linestyle="dashed", color="orange")

    plt.show()

def quick_simulation():
    circuit1 = 'cgtrack2'
    circuit2 = 'etrack3'
    server_forza = Server(circuit1)
    server_forza.setDaemon(True)
    server_forza.start()
    server_wheel = Server(circuit2)
    server_wheel.setDaemon(True)
    server_wheel.start()
    time.sleep(10)

    base_path=os.path.realpath(os.path.dirname(__file__))
    param_path=os.path.join(base_path,"parameters")

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
        f=open(os.path.join(param_path,"DE_96150.60.810/trained_params_15_gen"),"r")
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

    exit()

if __name__ == "__main__":
    quick_simulation()