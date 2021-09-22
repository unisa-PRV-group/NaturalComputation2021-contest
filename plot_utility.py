## FUNZIONE PER PLOTTARE BEST, AVG E STDDEV DELLA FITNESS GENERAZIONE PER GENERAZIONE ##

import matplotlib.pyplot as plt
import json
import os
import numpy as np

def plot_results(path_to_file):
    #recover history
    f=open(path_to_file,"r")
    data = json.load(f)
    f.close()

    best = data["best"]
    avgs = data["avg"]
    stddevs = data["stddev"]

    max_gens = len(best)
    base_path=os.path.realpath(os.path.dirname(__file__))
    fig_path=os.path.join(base_path,"doc")

    # plot convergence
    plt.title("Convergence")
    plt.plot(list(range(1,max_gens+1,1)), best)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.yscale("log")
    plt.xlim((1,max_gens))
    #plt.show()
    plt.savefig(os.path.join(fig_path,"exp6","fmin.png"))

    plt.clf()

    # plot avg per gen
    plt.title("Fitness avg per gen")
    plt.plot(list(range(1,max_gens+1,1)), avgs)
    plt.xlabel("Generation")
    plt.ylabel("Fitness avg")
    plt.yscale("log")
    plt.xlim((1,max_gens))
    #plt.show()
    plt.savefig(os.path.join(fig_path,"exp6","avg.png"))

    plt.clf()

    # plot stddev per gen
    plt.title("Fitness stddev per gen")
    plt.plot(list(range(1,max_gens+1,1)), stddevs)
    plt.xlabel("Generation")
    plt.ylabel("Fitness stddev")
    plt.yscale("log")
    plt.xlim((1,max_gens))
    #plt.show()
    plt.savefig(os.path.join(fig_path,"exp6","std.png"))

def plot_damage():
    damages = [sum([1668, 2638, 1123, 0, 2700, 2268, 344])/7, sum([9, 2908, 7, 16, 2371, 1934, 718])/7,
                sum([0, 236, 436, 0, 3456, 1379, 224])/7, sum([6, 435, 1688, 0, 1294, 3778, 368])/7
    ]
    fig, ax = plt.subplots()
    exps = ["Default", "2th", "5th", "6th"]
    ax.bar(exps,damages)
    ax.set_xlabel('Experiments')
    ax.set_ylabel('Average damage')
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(("Default", "2th", "5th", "6th"))
    plt.show()

plot_results(os.path.join(os.path.realpath(os.path.dirname(__file__)),"results/DE_240100.60.810/logs_45_gen_2"))