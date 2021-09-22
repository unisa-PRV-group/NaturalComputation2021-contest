import json
import os
from Server import Server
from client import race
import matplotlib.pyplot as plt
import time
from multiprocessing.pool import Pool

fname= "parameters_exp6"

base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
fig_path=os.path.join(base_path,"doc","speed_profiles")

def graphic_simulation():
    f=open(os.path.join(param_path,"DE_240100.60.810/{}".format(fname)),"r")
    race(3001,dict(json.load(f)),test=True)
    f.close()

def quick_simulation_with_speed_profile():
    suffix = "_opponents"
    ports = [3001,3002,3003,3004]
    circuits = ["forza", "wheel1", "gtrack","etrack"]
    circuits_name = ["Forza","Wheel1","CGTrack2","ETrack3"]

    for i,c in enumerate(circuits):
        s = Server(c)
        s.setDaemon(True)
        s.start()
        time.sleep(10)

        f=open(os.path.join(param_path,"default_parameters"),"r")
        params = dict(json.load(f))
        f.close()
        print(f"{c}: Default race started")
        results_def = race(ports[i],params,True)
        print(f"{c}: Default race finished")

        f=open(os.path.join(param_path,fname),"r")
        params=dict(json.load(f))
        f.close()
        print(f"{c}: Trained race started")
        results_trained = race(ports[i],params,True)
        print(f"{c}: Trained race finished")

        times = results_trained[1]
        speeds = results_trained[0]

        plt.title("Speed profile {}".format(circuits_name[i]))
        plt.plot(times, speeds, color="blue")
        plt.plot(results_def[1], [s for s in results_def[0]], color="orange")
        plt.legend(["Trained", "Default"])
        plt.ylabel("Speed (km/h)")
        plt.xlabel("Time (s)")
        plt.axvline(x=results_trained[2], linestyle="dashed", color="blue")
        plt.axvline(x=results_def[2], linestyle="dashed", color="orange")

        plt.savefig(os.path.join(fig_path,f"{circuits_name[i]}{suffix}.png"))

        plt.clf()

        s.stop(True)

    exit()

if __name__ == "__main__":
    quick_simulation_with_speed_profile()