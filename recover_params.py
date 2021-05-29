import os

def recover_params(path):
    all_files = os.listdir(path)

    found=[]

    for m in all_files:
        found.append(int(m.split("_")[1]))

    if len(found)>0: 
        choosed = max(found)
        return "logs_{}_gen".format(choosed)
    
    return ""