import os
import yaml
from datetime import datetime
import logging
import re
import io

class FocusMode(object):
    
    def __init__(self):        
    
        with open("focusmode_conf.yaml","r") as f:
            self.CONFIGS = yaml.safe_load(f)
    
        self.runtime_tpye       = self.CONFIGS["RUNTIMETYPE"]
        self.log_file_runtime   = self.CONFIGS["LOGFILE"][self.runtime_tpye]
        self.REDIRECT_BACK_IP   = self.CONFIGS["REDIRECT_BACK_IP"]
        self.HOST_FILE_PATH     = self.CONFIGS["HOST_FILE_PATH"]
        self.ENVIRON_VAR_NAME   = self.CONFIGS["ENVIRON_VAR_NAME"]
        self.SITELIST: list     = list(self.CONFIGS["SITELIST"].values())    
        self.ip_pattern         = "^(" + self.REDIRECT_BACK_IP + ")"
        self.url_pattern        = r"www\.[\S]+?\.[a-z]{2,4}"
    
        logging.basicConfig(format="[%(asctime)s][%(levelname)s]>%(message)s", filename=self.log_file_runtime, level=logging.DEBUG)
    
    def refreshConfigs(self):
        with open("focusmode_conf.yaml","r") as f:
            self.CONFIGS = yaml.safe_load(f)
            
        self.REDIRECT_BACK_IP    = "87.248.114.11"
        self.SITELIST: list      = list(CONFIGS["SITELIST"].values())
        
    def processEnvironVar(self,environ_copy: dict) -> str:
        environ_var = ""        
        if self.ENVIRON_VAR_NAME not in environ_copy.keys():
            logging.warning("FOCUSMODECONTROL not detected in Environment Variables. App will run in mode: Normal")
            return "Normal"
        if environ_copy[self.ENVIRON_VAR_NAME] not in ("Normal","Focus","Free"):
            logging.warning("Env var FOCUSMODECONTROL has a invalid value. Valid values: Focus,Free,Normal. Will ignore and presume: Normal")
            return "Normal"    
        return environ_copy[self.ENVIRON_VAR_NAME]    
    
    def isWorkingHours(self,time_stamp:datetime) -> bool:
        if time_stamp.isoweekday() < 6:
            if 9 < time_stamp.hour < 19:
                return True
        return False
    
    def computeFocusMode(self, environment_var:str, time_stamp) -> str:
        mode = ""    
        if environment_var == "Normal":
            mode = "Focus" if self.isWorkingHours(time_stamp) else "Free"
        else:
            mode = environment_var    
        return mode
    
    def getUrlFromString(self, target_string: str) -> str:        
        return re.findall(self.url_pattern, target_string)[0]  
    
    def isRedirectIpAtStartOfLine(self,line):
        return re.findall(self.ip_pattern, line)      
    
    def checkMissingRedirectsFromFile(self, file_stream, target_urls: dict) -> list:
        urls_in_file: list   = []        
        for line in file_stream.readlines():        
            if self.isRedirectIpAtStartOfLine(line):                    
                urls_in_file.append(self.getUrlFromString(line)) 
        file_stream.seek(0)
        return list(set(target_urls) - set(urls_in_file))
        
    def appendNewLineIfCase(self,file_stream):
        stream_length = file_stream.seek(0,os.SEEK_END)
        file_stream.seek(stream_length - 1)
        if file_stream.read() != "\n":
            file_stream.seek(0,os.SEEK_END)
            file_stream.write("\n")
            
    def appendRedirects(self, file_stream, url_list: list):        
        self.appendNewLineIfCase(file_stream)
        file_stream.seek(0,os.SEEK_END)
        for url in url_list:
            file_stream.write(f"{self.REDIRECT_BACK_IP} {url}\n")
        file_stream.seek(0)
        
    def removeRedirects(self, file_stream, url_list: list):
        new_file_txt: str= ""
        for line in file_stream.readlines():
            if self.isRedirectIpAtStartOfLine(line) and self.getUrlFromString(line):
                continue
            else:
                new_file_txt += line
        try:
            file_stream.seek(0)
            file_stream.truncate(0)
        except Exception as e:
            logging.ERROR(f"Can't empty the file! System error:{e.message}")
        else:
            file_stream.write(new_file_txt)            
    
    def runAppRoutine(self):
        environment_vars    = os.environ.copy()
        focusmode_var       = self.processEnvironVar(environment_vars)
        focus_mode          = self.computeFocusMode(focusmode_var, datetime.now())
        
        if focus_mode == "Focus":
            with open(self.HOST_FILE_PATH, "r") as f:
                urls_to_write = self.checkMissingRedirectsFromFile(f, self.SITELIST)
            if urls_to_write:
                logging.info("URLs need to be added to the host file.")
                with open(self.HOST_FILE_PATH,"a+") as f:
                    self.appendRedirects(f, urls_to_write)
                os.popen("ipconfig /flushdns")
        
        if focus_mode == "Free":
            logging.info("Host file will be scanned to remove any URLs from the list.")
            with open(self.HOST_FILE_PATH,"r+") as f:                
                self.removeRedirects(f, self.SITELIST)
            os.popen("ipconfig /flushdns")        

if __name__ == '__main__':
    service = FocusMode()
    service.runAppRoutine()   