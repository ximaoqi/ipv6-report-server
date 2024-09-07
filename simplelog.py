#!/usr/bin/python3
import time

def getNowDate_format ():
    return time.strftime("%Y-%m-%d",time.localtime())

def getNowDate_num ():
    return time.strftime("%Y%m%d",time.localtime())

def getNow() :
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

def getNowSec() -> int:
    return int(time.time())

def getNowNs() -> int :
    return time.time_ns()

CLOSE = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4
DEBUG = 5

class LogHandle :

    def __init__( self, out_logfile, log_level = ERROR, date_rotate_flag = False, time_stamp_flag = False) :
        #check must parameter
        if not isinstance(log_level, int) :
            raise ValueError("Plese use simple_log.CLOSE ~ simple_log.DEBUG.")
        elif log_level < -1 or log_level > 5 :
            raise ValueError("Plese use simple_log.CLOSE ~ simple_log.DEBUG.")

        if not isinstance(date_rotate_flag, bool) :
            raise ValueError("The date_rotate_flag must is bool type.")
        
        if not isinstance(time_stamp_flag, bool) :
            raise ValueError("The time_stamp_flag must is bool type.")
        
        #init
        self.__date_rotate_flag = date_rotate_flag
        self.__loglevel = log_level
        self.__source_filename = out_logfile
        self.__time_stamp = time_stamp_flag
        self.__rotate_date = getNowDate_num()
        #test value
        #self.__trotate = self.__rotate_date

        #set outfile 
        if self.__date_rotate_flag :
            self.__setRotateOutFileName()
        else :
            self.__outfile = self.__source_filename
        self.__setOutFun()

        #set out point
        self.__out_pt = open(self.__outfile, "a")
        self.__level_list = ["[CLOSE]", "[INFO]", "[WARNING]", "[ERROR]", "[CRITICAL]", "[DEBUG]"]   

    def __del__(self) :
        self.__out_pt.close()

#insede fun
    def __setRotateOutFileName(self) :    
        dot_index = self.__source_filename.rfind('.')
        if dot_index != -1 :
             self.__outfile = self.__source_filename[0:dot_index] + "_" + self.__rotate_date + self.__source_filename[dot_index:]
        else :
             self.__outfile = self.__source_filename + "_" + self.__rotate_date

    def __rotateProcess(self) :
        if self.__rotate_date != getNowDate_num() :
            self.__rotate_date = getNowDate_num()
            self.__setRotateOutFileName()
            self.__out_pt.close()
            self.__out_pt = open(self.__outfile, "a")

    #test fun
    '''
    def __rotateProcess_1(self) :
        if self.__rotate_date != self.__trotate :
            self.__rotate_date = self.__trotate
            self.__setRotateOutFileName()
            self.__out_pt.close()
            self.__out_pt = open(self.__outfile, "a") 
    '''       

    def __setOutFun(self) :
        if self.__loglevel >= 5 :
            if self.__time_stamp and self.__date_rotate_flag :
                self.__debug = self.__roteOutWithTime
            elif self.__time_stamp :
                self.__debug = self.__outWithTime
            elif self.__date_rotate_flag :
                self.__debug = self.__justRotaOut
            else :
                self.__debug = self.__justOut
        else :
            self.__debug = self.__nullFun

        if self.__loglevel != 0 :
            if self.__time_stamp and self.__date_rotate_flag :
                self.__critical = self.__roteCriticalWithTime
            elif self.__time_stamp :
                self.__critical = self.__criticalWithTime
            elif self.__date_rotate_flag :
                self.__critical = self.__justRotaCritical
            else :
                self.__critical = self.__justCritical
        else :
            self.__critical = self.__nullFun

        if self.__loglevel >= 3 :
            if self.__time_stamp and self.__date_rotate_flag :
                self.__error = self.__roteOutWithTime
            elif self.__time_stamp :
                self.__error = self.__outWithTime
            elif self.__date_rotate_flag :
                self.__error = self.__justRotaOut
            else :
                self.__error = self.__justOut
        else :
            self.__error = self.__nullFun

        if self.__loglevel >= 2 :
            if self.__time_stamp and self.__date_rotate_flag :
                 self.__waring = self.__roteOutWithTime
            elif self.__time_stamp :
                 self.__waring = self.__outWithTime
            elif self.__date_rotate_flag :
                 self.__waring = self.__justRotaOut
            else :
                 self.__waring = self.__justOut
        else :
             self.__waring = self.__nullFun

        if self.__loglevel >= 1 :
            if self.__time_stamp and self.__date_rotate_flag :
                 self.__info = self.__roteOutWithTime
            elif self.__time_stamp :
                 self.__info = self.__outWithTime
            elif self.__date_rotate_flag :
                 self.__info = self.__justRotaOut
            else :
                 self.__info = self.__justOut
        else :
             self.__info = self.__nullFun

    
# base out fun
    def toLog(self, out_info) :
        count = 0
        while (count < 5) :
            try :
                 self.__out_pt.write(out_info)
            except ValueError :
                time.sleep(0.01)
                count = count + 1
            else :
                count = 6

        if count == 5 :
            raise ValueError

# out fun
    def toLogOnLine(self, out_info) :
        self.toLog(out_info + '\n')

    def toLogOnLineWithTime(self, out_info) :
        self.toLogOnLine(getNow() + " " + out_info)

    def toLogWithTime(self, out_info) :
        self.toLog(getNow() + " " + out_info)

    def info(self, out_info) :
        self.__info(out_info, "[INFO]")

    def waring(self, out_info) :
        self.__waring(out_info, "[WARING]")

    def error(self, out_info) :
        self.__error(out_info, "[ERROR]")

    def critical(self, out_info) :
        self.__critical(out_info)

    def debug(self, out_info) :
        self.__debug(out_info, "[DEBUG]")




# __out function
    def __justOut(self, out_info, level_info) :
        self.toLogOnLine(level_info + out_info)

    def __outWithTime(self, out_info, level_info) :
        self.toLogOnLine(getNow() + " " + level_info + out_info)

    def __justRotaOut(self, out_info, level_info) :
        self.__rotateProcess()
        self.toLogOnLine(level_info + out_info)

    def __roteOutWithTime(self, out_info, level_info) :
        self.__rotateProcess()
        self.toLogOnLine(getNow() + " " + level_info + out_info)

    def __nullFun(self, out_info, level_info) :
        pass


#__out critical function
    def __justCritical(self, out_info) :
        self.toLogOnLine(" [CRITICAL]" + out_info)
        exit(0)

    def __criticalWithTime(self, out_info) :
        self.toLogOnLine(getNow() + " [CRITICAL]" + out_info)
        exit(0)

    def __justRotaCritical(self, out_info) :
        self.__rotateProcess()
        self.toLogOnLine(" [CRITICAL]" + out_info)
        exit(0)

    def __roteCriticalWithTime(self, out_info) :
        self.__rotateProcess()
        self.toLogOnLine(getNow + " [CRITICAL]" + out_info)
        exit(0)

# get objet info fun
    def getOutFile(self) :
        return self.__outfile
    
    def getLogLevel(self) :
        return self.__level_list[self.__loglevel]
    
    def getDateRotateFlag(self) :
        return self.__date_rotate_flag
    
    def getTimeStampFlag(self) :
        return self.__time_stamp
    
# set objet parameter
    def changeOutFile(self, filename) :
        if self.__source_filename != filename :
            self.__source_filename = filename
            if self.__date_rotate_flag :
                self.__setRotateOutFileName()
            else :
                self.__outfile = self.__source_filename

            self.__out_pt.close()
            self.__out_pt = open(self.__outfile, "a")

    def changeLogLevel(self, log_level) :
        if not isinstance(log_level, int) :
            raise ValueError("Plese use simple_log.CLOSE ~ simple_log.DEBUG.")
        elif log_level < -1 or log_level > 5 :
            raise ValueError("Plese use simple_log.CLOSE ~ simple_log.DEBUG.")
        
        if self.__loglevel != log_level :
            self.__loglevel = log_level
            self.__setOutFun()

    def changeDate_rotate_flag(self, date_rotate_flag) :
        if not isinstance(date_rotate_flag, bool) :
            raise ValueError("The date_rotate_flag must is bool type.")
        
        if self.__date_rotate_flag != date_rotate_flag :
            self.__date_rotate_flag = date_rotate_flag
            if self.__date_rotate_flag :
                self.__rotate_date = getNowDate_num()
                self.__setRotateOutFileName()
            else :
                self.__outfile = self.__source_filename
            
            self.__out_pt.close()
            self.__out_pt = open(self.__outfile, "a")
            self.__setOutFun()
        
    def changeTimeStampFlag(self, time_stamp_flag) :
        if not isinstance(time_stamp_flag, bool) :
            raise ValueError("The time_stamp_flag must is bool type.")
        
        if self.__time_stamp != time_stamp_flag :
            self.__time_stamp = time_stamp_flag
            self.__setOutFun()

    #fflush
    def fflush(self) :
        self.__out_pt.flush()