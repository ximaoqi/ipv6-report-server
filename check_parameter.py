#!/usr/bin/python3
import os
import ipaddress

def checkNoneType (obj):
    try :
        obj_lens = len(obj)
    
    except TypeError :
        return -1
    
    if obj_lens <= 0 :
        return -1

    return obj_lens
    

def checkStr (obj) :
    if not isinstance(obj, str) :
        return -1   
    return 0

def checkBool(obj) :
    if not isinstance(obj, bool) :
        return -1   
    return 0
    
def checkStrDecNum(obj) :
        if not isinstance(obj, str) :
            return -1 
        
        try :
            int(obj)
        except ValueError :
            return -1       
        return 0

def checkStrBinNum(obj) :
        if not isinstance(obj, str) :
            return -1 

        try :
            int(obj, 2)
        except ValueError :
            return -1        
        return 0

def checkStrOctNum(obj) :
        if not isinstance(obj, str) :
            return -1 

        try :
            int(obj, 8)
        except ValueError :
            return -1        
        return 0

def checkStrHexNum(obj) :
        if not isinstance(obj, str) :
            return -1 

        try :
            int(obj, 16)
        except ValueError :
            return -1        
        return 0


def checkStrIPv6(obj:str) ->int :
    if not isinstance(obj, str) :
        return -1 
    try :
        ipaddress.IPv6Address(obj)
    except ValueError :
        return -1
    
    return 0   

def checkStrIPv4(obj:str) ->int :
    if not isinstance(obj, str) :
        return -1 
    try :
        ipaddress.IPv4Address(obj)
    except ValueError :
        return -1
    
    return 0   

def checkStrIPv4_c(obj) :
    if checkStr(obj) == -1 :
        return -1
    
    start = 0
    int_sub = 0
    while (True) :
        end = obj.find('.', start)
        if end == -1 :
            if int_sub != 3 :
                return -1
            else :
                try :
                    num = int(obj[start:])
                except ValueError :
                    return -1
                if num <0 or num > 255 :
                    return -1
                return 0

        else :
            if int_sub > 3 :
                return -1
            try :
                num = int(obj[start:end])
            except ValueError :
                return -1
            
            if num <0 or num > 255 :
                return -1
                       
        start = end + 1
        int_sub = int_sub + 1

def checkStrIPv6_c(obj: str) ->int :
    if not isinstance(obj, str) :
        return -1
    start = 0
    int_sub = 0
    colon_sub = 0
    colon_flag = 0
    while (True) :
        end = obj.find(':', start)
        if end == -1 :
            if colon_sub < 2 or colon_sub > 7 :
                return -1
            elif colon_flag == 2 :
                return 0
            else :
                try :
                    num = int(obj[start:], 16)
                except ValueError :
                    if colon_flag == 1 and int_sub > 0 :
                        return 0
                    return -1
                
                if num < 0 or num > 0xffff :
                    return -1
                else :
                    return 0
        
        elif end == start :
            colon_sub = colon_sub + 1
            start = end + 1
            if colon_flag < 2 :
                colon_flag = colon_flag + 1
                continue
            else :
                return -1
                            
        else :
            if colon_sub >= 8 :
                return -1
            
            try :
                num = int(obj[start:end], 16)
            except ValueError :
                return -1
            
            if num < 0 or num > 0xffff :
                return -1
            else :
                start = end + 1
                int_sub = int_sub + 1
                colon_sub = colon_sub + 1
        

def checkPort(obj) :
    if not isinstance(obj, int) :
        return -1
    
    if obj <= 0 or obj > 65535 :
        return -1    
    return 0

def checkUint32(obj) :
    if not isinstance(obj, int) :
        return -1
    
    if obj <= 0 or obj > 4294967295 :
        return -1
    return 0

def checkPath() :
    filepath = os.path.dirname(os.path.abspath(__file__))
    pwd = os.getcwd()
    if not filepath == pwd :
        os.chdir(filepath)
