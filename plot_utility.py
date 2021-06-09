## FUNZIONE PER PLOTTARE BEST, AVG E STDDEV DELLA FITNESS GENERAZIONE PER GENERAZIONE ##

import matplotlib.pyplot as plt
import json
import os

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
    plt.savefig(os.path.join(fig_path,"{}_gen_convergence.png".format(max_gens)))

    plt.clf()

    # plot avg per gen
    plt.title("Fitness avg per gen")
    plt.plot(list(range(1,max_gens+1,1)), avgs)
    plt.xlabel("Generation")
    plt.ylabel("Fitness avg")
    plt.yscale("log")
    plt.xlim((1,max_gens))
    #plt.show()
    plt.savefig(os.path.join(fig_path,"{}_gen_avg.png".format(max_gens)))

    plt.clf()

    # plot stddev per gen
    plt.title("Fitness stddev per gen")
    plt.plot(list(range(1,max_gens+1,1)), stddevs)
    plt.xlabel("Generation")
    plt.ylabel("Fitness stddev")
    plt.yscale("log")
    plt.xlim((1,max_gens))
    #plt.show()
    plt.savefig(os.path.join(fig_path,"{}_gen_stddev.png".format(max_gens)))

plot_results(os.path.join(os.path.realpath(os.path.dirname(__file__)),"results/DE_240100.60.810/logs_45_gen_2"))