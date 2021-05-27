import json
import os
from Server import Server
from client import race

server_forza = Server('wheel1')
server_forza.setDaemon(True)
server_forza.start()
base_path=os.path.realpath(os.path.dirname(__file__))
param_path=os.path.join(base_path,"parameters")
f=open(os.path.join(param_path,"trained_params_10"),"r")
print(race(3002,dict(json.load(f))))
f.close()
exit()