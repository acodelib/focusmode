"""
Service starts.
Service checks every 10 seconds:
    -- what day of week and and time it is.
    -- Environment variable ["FocusMode"] for overides: Normal, Focus, Free

If Environment var doesn't exist or is Normal or Var 

"""


import os
from datetime import datetime
import logging
from collections import ChainMap
logging.basicConfig(format="[%(asctime)s][%(levelname)s]>%(message)s", filename="focusmode_log_test.txt", level=logging.DEBUG)


logging.info("hi")

import yaml

str = open("focusmode_conf.yaml", "r")

configs = yaml.safe_load(str)
print(configs)

opt = ChainMap(configs)
print(opt["SITELIST"])
for k,v in opt["SITELIST"].items():
    print(v)


#check time and day of week
#look for overides

#update 

#cli_stream = os.popen("ipconfig /flushdns")


#os.environ["FocusMode"] = "sometest"



with open("focusmode_conf.yaml","r") as f:
    configs = yaml.safe_load(f)
runtime_tpye     = configs["RUNTIMETYPE"]
log_file_runtime = configs["LOGFILE"][runtime_tpye]

print(log_file_runtime)