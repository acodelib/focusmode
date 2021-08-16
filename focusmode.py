import os
import yaml
from datetime import datetime
import logging
import re



with open("focusmode_conf.yaml","r") as f:
    CONFIGS = yaml.safe_load(f)
runtime_tpye     = CONFIGS["RUNTIMETYPE"]
log_file_runtime = CONFIGS["LOGFILE"][runtime_tpye]

REDIRECT_BACK_IP    = "87.248.114.11"
HOST_FILE_PATH      = "C:/Windows/System32/drivers/etc/hosts"
SITELIST: list      = list(CONFIGS["SITELIST"].values())
    

logging.basicConfig(format="[%(asctime)s][%(levelname)s]>%(message)s", filename=log_file_runtime, level=logging.DEBUG)

print(globals())
def processEnvironVar(environ_copy: dict) -> str:
    environ_var = ""
    if 'FOCUSMODECONTROL' not in environ_copy.keys():
        logging.warning("FOCUSMODECONTROL not detected in Environment Variables. App will run in mode: Normal")
        return "Normal"
    if environ_copy["FOCUSMODECONTROL"] not in ("Normal","Focus","Free"):
        logging.warning("Env var FOCUSMODECONTROL has a invalid value. Valid values: Focus,Free,Normal. Will ignore and presume: Normal")
        return "Normal"    
    return environ_copy["FOCUSMODECONTROL"]    

def isWorkingHours(time_stamp:datetime) -> bool:
    if time_stamp.isoweekday() < 6:
        if 9 < time_stamp.hour < 19:
            return True
    return False

def computeFocusMode(environment_var:str, time_stamp) -> str:
    mode = ""    
    if environment_var == "Normal":
        mode = "Focus" if isWorkingHours(time_stamp) else "Free"
    else:
        mode = environment_var    
    return mode

def getUrlFromString(target_string: str) -> str:
    url_pattern = r"www\.[\S]+?\.[a-z]{2,4}"
    return re.findall(url_pattern, target_string)[0]
    

def checkMissingRedirectsFromFile(file_stream, target_urls: dict) -> list:
    urls_in_file: list   = []
    ip_pattern = "^(" + REDIRECT_BACK_IP + ")"
    
    for line in file_stream.readlines():        
        if re.findall(ip_pattern, line):                    
            urls_in_file.append(getUrlFromString(line)) 
    
    return list(set(target_urls) - set(urls_in_file))
        
def appendRedirects(file_stream, url_list: list):        
    file_stream.seek(0,os.SEEK_END)    
    for url in url_list:
        file_stream.write(f"{REDIRECT_BACK_IP} {url}\n")
        
def removeRedirects(the_file: str, url_list: list):
    pass

def runAppRoutine():
    environment_vars    = os.environ.copy()
    focusmode_var       = processEnvironVar(environment_vars)
    focus_mode          = computeFocusMode(focusmode_var, datetime.now())
    
    if focus_mode == "Focus":
        with open(HOST_FILE_PATH) as f:
            urls_to_write = checkMissingRedirectsFromFile(f, SITELIST)
        if urls_to_write:
            with open(HOST_FILE_PATH) as f:
                appendRedirects(f, urls_to_write)
    
    if focus_mode == "Free":
        removeRedirects()
        
