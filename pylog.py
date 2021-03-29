# -*- coding: utf-8 -*-
import os
import time
import logging
import inspect
from logging.handlers import RotatingFileHandler
from datetime import datetime
import threading
import G_Function as vs 
from concurrent_log_handler import ConcurrentRotatingFileHandler



log_set_flag=0

def check_dir(path_set):
    PATH={
            "info":"/logs/info",
            "buslog":"/logs/buslog",
            "error":"/logs/error"
            }
    if path_set!='':
        if path_set in PATH:
            logs_dir=vs.Config["proj_path"]+PATH[path_set]
        else:           
            logs_dir=vs.Config["proj_path"]+"/logs/"+path_set
            PATH[path_set]=logs_dir
    for path in PATH:
        PATH[path]=logs_dir
        if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
            pass
        else:
            os.mkdir(logs_dir)
    
    return PATH[path_set]

class TNLog(object):
    
    def __init__(self,file_name='',mode=0,level=logging.NOTSET):
        self.__loggers = {}
        self._mode=mode
        self._file_name=file_name
        #dir_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
        #file_name=file_name+' '+dir_time
        if self._mode==0:           
            self.handlers = {   
                logging.INFO: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                logging.ERROR: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                }
        else:   
            self.handlers = {#logging.NOTSET: os.path.join(check_dir('notset'), 'notset_%s.log'%dir_time),   
                logging.DEBUG: os.path.join(check_dir('debug'), '%s.log'%self._file_name),   
                logging.INFO: os.path.join(check_dir('buslog'), '%s.log'%self._file_name),   
                #logging.WARNING: os.path.join(check_dir('warning'), 'warning_%s.log'%file_name),  
                logging.ERROR: os.path.join(check_dir('error'), '%s.log'%self._file_name),   
                #logging.CRITICAL: os.path.join(check_dir('cri'), 'critical_%s.log'%file_name),
                }
       
        logLevels = self.handlers.keys()

        for level in logLevels:
            path = os.path.abspath(self.handlers[level])
            #self.handlers[level] = RotatingFileHandler(path, maxBytes=1024 * 1024 * 150, backupCount=2, encoding='utf-8')
            self.handlers[level] = ConcurrentRotatingFileHandler(path, maxBytes=1024 * 1024 * 150, backupCount=2, encoding='utf-8')

        #if log_set_flag==0:
        for level in logLevels:
            logger = logging.getLogger(str(level))
            logger.handlers.clear()
            #logger.handlers.clear()
            logger.propagate = False
            logger.addHandler(self.handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level: logger})
        
    def printfNow(self):
        #return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


    def getLogMessage(self, level, message):
        #frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        
        return "[%s]%s" % (self.printfNow(),message)

        #return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    
    def write(self, message):
        #if self.mode==0:message = self.getLogMessage("debug", message);self.__loggers[logging.DEBUG].debug(message)
        #else:
        message = self.getLogMessage("info", message);self.__loggers[logging.INFO].info(message)


    def error(self, message):      
        #if self.mode==0:message = self.getLogMessage("debug", message);self.__loggers[logging.DEBUG].debug(message)
        #else:
        message = self.getLogMessage("error", message);self.__loggers[logging.ERROR].error(message)

    def debug(self, message):
        message = self.getLogMessage("debug", message)

        self.__loggers[logging.DEBUG].debug(message)

    def close(self):
        logging.shutdown()






class wxll_Log(object):
    def __init__(self,file_name='',mode=0,level=logging.NOTSET):
        self.__loggers = {}
        self._mode=mode
        self._file_name=file_name

    def file_handle(self):
               
        if self._mode==0:           
            self.handlers = {   
                logging.INFO: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                logging.ERROR: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                logging.DEBUG: os.path.join(check_dir('debug'), '%s.log'%self._file_name)
                }
        else:   
            self.handlers = {#logging.NOTSET: os.path.join(check_dir('notset'), 'notset_%s.log'%dir_time),   
                logging.DEBUG: os.path.join(check_dir('debug'), '%s.log'%self._file_name),   
                logging.INFO: os.path.join(check_dir('buslog'), '%s.log'%self._file_name),   
                #logging.WARNING: os.path.join(check_dir('warning'), 'warning_%s.log'%file_name),  
                logging.ERROR: os.path.join(check_dir('error'), '%s.log'%self._file_name) 
                #logging.CRITICAL: os.path.join(check_dir('cri'), 'critical_%s.log'%file_name),
                }
       
        logLevels = self.handlers.keys()
    
        for level in logLevels:
            path = os.path.abspath(self.handlers[level])
            self.handlers[level] = RotatingFileHandler(path, maxBytes=1024 * 1024 * 150, backupCount=2, encoding='utf-8')


        #if log_set_flag==0:
        for self.level in logLevels:
            logger = logging.getLogger(str(self.level))
            logger.handlers.clear()
            #logger.handlers.clear()
            logger.propagate = False
            logger.addHandler(self.handlers[self.level])
            logger.setLevel(self.level)
            self.__loggers.update({self.level: logger})
        
    def printfNow(self):
        #return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


    def getLogMessage(self, level, message):
        #frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        self.file_handle()
        return "[%s]%s" % (self.printfNow(),message)

        #return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    
    def write(self, message):
                
        message = self.getLogMessage("info", message);self.__loggers[logging.INFO].info(message)


    def error(self, message):      
        #if self.mode==0:message = self.getLogMessage("debug", message);self.__loggers[logging.DEBUG].debug(message)
        #else:

        message = self.getLogMessage("error", message);self.__loggers[logging.ERROR].error(message)

    def debug(self, message):
 
        message = self.getLogMessage("debug", message)

        self.__loggers[logging.DEBUG].debug(message)
    """

    def info(self, message):
        message = self.getLogMessage("info", message)

        self.__loggers[logging.INFO].info(message)

    def warning(self, message):
        message = self.getLogMessage("warning", message)

        self.__loggers[logging.WARNING].warning(message)
    def critical(self, message):
        message = self.getLogMessage("critical", message)

        self.__loggers[logging.CRITICAL].critical(message)
    """



class wxll_Log_new(object):
    def __init__(self,file_name='',mode=0,level=logging.NOTSET):
        self.__loggers = {}
        self._mode=mode
        self._file_name=file_name
        self.R = threading.Lock()  
    def file_handle(self):       
        if self._mode==0:           
            self.handlers = {   
                logging.INFO: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                logging.ERROR: os.path.join(check_dir('debug'), '%s.log'%self._file_name),
                logging.DEBUG: os.path.join(check_dir('debug'), '%s.log'%self._file_name)
                }
        else:   
            self.handlers = {#logging.NOTSET: os.path.join(check_dir('notset'), 'notset_%s.log'%dir_time),   
                logging.DEBUG: os.path.join(check_dir('debug'), '%s.log'%self._file_name),   
                logging.INFO: os.path.join(check_dir('buslog'), '%s.log'%self._file_name),   
                #logging.WARNING: os.path.join(check_dir('warning'), 'warning_%s.log'%file_name),  
                logging.ERROR: os.path.join(check_dir('error'), '%s.log'%self._file_name) 
                #logging.CRITICAL: os.path.join(check_dir('cri'), 'critical_%s.log'%file_name),
                }
       
        logLevels = self.handlers.keys()
    
        for level in logLevels:
            path = os.path.abspath(self.handlers[level])
            self.handlers[level] = RotatingFileHandler(path, maxBytes=1024 * 1024 * 150, backupCount=2, encoding='utf-8')


        #if log_set_flag==0:
        for self.level in logLevels:
            logger = logging.getLogger(str(self.level))
            logger.handlers.clear()
            #logger.handlers.clear()
            logger.propagate = False
            logger.addHandler(self.handlers[self.level])
            logger.setLevel(self.level)

            self.__loggers.update({self.level: logger})
        
    def printfNow(self):
        #return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


    def getLogMessage(self, level, message):
        #frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        self.file_handle()
        return "[%s]%s" % (self.printfNow(),message)

        #return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    
    def write(self, message):
        #if self.mode==0:message = self.getLogMessage("debug", message);self.__loggers[logging.DEBUG].debug(message)
        #else:
        self.R.acquire()
        self.file_handle()        
        self.__loggers[logging.INFO].info(message)
        self.R.release()


    def error(self, message):      
        #if self.mode==0:message = self.getLogMessage("debug", message);self.__loggers[logging.DEBUG].debug(message)
        #else:
        self.file_handle()
        self.__loggers[logging.ERROR].error(message)

    def debug(self, message):
        self.file_handle()        
        self.__loggers[logging.DEBUG].debug(message)
    """

                 
        while not self.exit_requested:
            if not self.logqueue.empty():
    def info(self, message):
        message = self.getLogMessage("info", message)

        self.__loggers[logging.INFO].info(message)

    def warning(self, message):
        message = self.getLogMessage("warning", message)

        self.__loggers[logging.WARNING].warning(message)
    def critical(self, message):
        message = self.getLogMessage("critical", message)

        self.__loggers[logging.CRITICAL].critical(message)
    """







if __name__ == "__main__":
    logger = TNLog()
    