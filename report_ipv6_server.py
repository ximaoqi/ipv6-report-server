#!/usr/bin/python3
import socket
import ssl
import json
import threading
import atexit

#customer lib
import simplelog
import check_parameter

PCODE = ""
REPROT_DICT = {}
THRAED_QUEUE = []
COND_LOCK = threading.Lock()
JOIN_COND = threading.Condition(COND_LOCK)

def main() :
    #config file path
    CONFIG_FILE = "server_config.json"


    #check path
    check_parameter.checkPath()

    #open config file
    try :
        config = json.load(open(CONFIG_FILE, "r"))
    except FileNotFoundError :
        print("Can't open config file.\n")
        exit(-1)
    except json.decoder.JSONDecodeError :
        print("The configuration file is damaged.\n")
        exit(-1)
    except PermissionError :
        print("Can't open config file.\n")
        exit(-1)

    #format config
    server_ip = config.get("server")
    server_port = config.get("port")
    pcode = config.get("pcode")
    logfile = config.get("logfile")
    cerfile = config.get("crefile")
    keyfile = config.get("keyfile")
    listen_num = config.get("listen")
    timeout = config.get("net_timeout")
    savefile = config.get("savefile")
    
    #open log handle
    log = simplelog.LogHandle(logfile, time_stamp_flag=True)

    #check config parmeter
    if check_parameter.checkStrIPv4(server_ip) == -1 :
        log.critical("The server address is unavailable.")

    if check_parameter.checkPort(server_port) == -1 :
        log.critical("The server port is unavailable.")

    if check_parameter.checkStr(pcode) == -1 :
        log.critical("The Pcode is unavailable.")
    
    global PCODE
    PCODE = pcode

    if check_parameter.checkStr(cerfile) == -1 :
        log.critical("The crefile is unavailable.")

    if check_parameter.checkStr(keyfile) == -1 :
        log.critical("The keyfile is unavailable.")
    
    if check_parameter.checkUint32(listen_num) == -1 :
        log.error("The listen num is unavailable, set default value is 1024.")
        listen_num = 1024

    if check_parameter.checkUint32(timeout) == -1 :
        log.error("The timeout is unavailable, set default value is 60.")
        timeout = 60

    #check save file
    if check_parameter.checkStr(savefile) == 1 :
        savefile = "save.json"
        log.error("The save file is unavailable, set default file.")

    try :
        save = json.load(open(savefile, "r"))
    except FileNotFoundError :
        log.error("The save file not found, do not load.")
    except json.decoder.JSONDecodeError:
        log.error("The configuration file is damaged, do not load.")
    except PermissionError :
        log.error("Can't open save file, do not load.")

    else :
        if len(save) == 0 :
            log.error("The save file is null, do not load.")
        else :
            #load save file
            log.info("Loading save.")
            loads = 0
            global REPROT_DICT
            for i in save :
                temp = save.get(i)
                if checkSaveInfo(temp) != 0 :
                    continue
                REPROT_DICT.update({i:temp})
                loads = loads + 1
            log.info("{} information have been loaded.".format(loads))

            


    #register exit fun for save dict to file
    atexit.register(atexit_save, savefile, log)



    #init ssl socket
    log.info("Init services.")
    contxet = ssl.SSLContext(ssl.PROTOCOL_TLS)
    try :    
        contxet.load_cert_chain(certfile= cerfile, keyfile= keyfile)
    except FileNotFoundError :
        log.critical("The crefile or keyfile not found.")
    except ssl.SSLError: 
        log.critical("The crefile and keyfile mismatching.")
    
    contxet.verify_mode = ssl.CERT_NONE

    server_ss = contxet.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side= True)
    try :
        server_ss.bind((server_ip, server_port))
    except OSError :
        log.critical("Binding address failed.")

    server_ss.listen(listen_num)
    log.info("The services status is ready.")

    #start join demon
    joindemon = JoinDemon(log)
    joindemon.start()

    #handle client connection
    while(True) :
        try :
            ss_client, client_add  = server_ss.accept()
        except ssl.SSLError :
            log.error("Wrong HTTP connection."  )
            continue
        except ConnectionResetError :
            log.error("Wrong connection reset.")
        except :
            log.error("Wrong connection.")
            continue

        ss_client.settimeout(timeout)
        server_thread = ServerThreading(ss_client, log)

        #add server thread to global queue list
        THRAED_QUEUE.append(server_thread)
        server_thread.start()

    joindemon.join()
    
class ServerThreading(threading.Thread) :
    def __init__(self, ssocket, log_handle) :
        super().__init__()
        self.__ssocket = ssocket
        self.__log_handle = log_handle
        self.__comflag = False
        self.__peerid = self.__ssocket.getpeername()[0]
        self.__peerport = self.__ssocket.getpeername()[1]
        self.__errflag = False

    def __verifyPcode(self) -> int:
        global PCODE
        try :
            buffer = json.loads(self.__ssocket.recv().decode())
        except TimeoutError :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Connection timeout, from address: {}:{}".format(self.__peerid, self.__peerport))
            self.__errflag = True
            return -1
        except json.decoder.JSONDecodeError :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Connection loss, from address: {}:{}".format(self.__peerid, self.__peerport))
            self.__errflag = True
            return -1
        except UnicodeDecodeError :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Buffer decode error, from address: {}:{}".format(self.__peerid, self.__peerport))
            self.__errflag = True
            return -1
        
        if buffer.get("pcode") != PCODE :
            self.__ssocket.send(json.dumps({"rcode" : -1, "rinfo": "The pcode mismatching."}).encode())
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "The pcode mismatching, from {}({}:{}).".format(buffer.get("name"), self.__peerid, self.__peerport))
            return -1
        
        self.__ssocket.send(json.dumps({"rcode" : 0, "rinfo": "Pcode matching."}).encode())
        self.__log_handle.info("[" + str(threading.get_native_id()) + "]" + "Pcode matching, request from {}({}:{}).".format(buffer.get("name"), self.__peerid, self.__peerport))
        return 0
    
    def __addIpv6ToDict(self, buffer :dict) :
        if self.__checkIpMsg(buffer) != 0 :
            self.__ssocket.send(json.dumps({"rcode" : -1, "rinfo": "Message format error."}).encode())
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Message format error, do not update information, from address {}:{}.".format(self.__peerid, self.__peerport))
            return -1

        global REPROT_DICT
        REPROT_DICT.update({buffer.get("name") : buffer})
        self.__ssocket.send(json.dumps({"rcode" : 0, "rinfo": "Report completed, and update to share dict."}).encode())

        self.__log_handle.info( "[" + str(threading.get_native_id()) + "]" + "Update {}({}:{}) information completed.".format(buffer.get("name"), self.__peerid, self.__peerport))
        return 0

    def __pushIpv6Dict(self, buffer :dict) :
        global REPROT_DICT
        lens = len(REPROT_DICT)
        if lens == 0 :
            msg = {"rcode": -2, "rinfo": "No information."}
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "No information, request from {}({}:{}).".format(buffer.get("name"), self.__peerid, self.__peerport))
        else :
            msg = {"rcode": 0}
            msg.update(REPROT_DICT)
            self.__log_handle.info( "[" + str(threading.get_native_id()) + "]" + "push information to {}({}:{}) for completed.".format(buffer.get("name"), self.__peerid, self.__peerport))

        self.__ssocket.send(json.dumps(msg).encode())
        if lens == 0 :
            return -2
        else :
            return 0
        
    def __sendErrorOp(self) :
        self.__ssocket.send(json.dumps({"rcode": -999, "rinfo": "Illegal operations."}).encode())
        return -999

    def __Op(self) :
        try :
            buffer = json.loads(self.__ssocket.recv().decode())
        except TimeoutError :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Connection timeout from {}:{}.".format(self.__peerid, self.__peerport))
            op_status = {"opcode": -2, "rcode": -2}
            return op_status
        except json.decoder.JSONDecodeError :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + "Connection loss from {}:{}.".format(self.__peerid, self.__peerport))
            op_status = {"opcode": -2, "rcode": -2}
            return op_status
        
        opcode = buffer.pop("opcode")
        if opcode == 2 :
            op_status = {"opcode": opcode, "rcode": self.__pushIpv6Dict(buffer)}
            return op_status
        
        elif opcode == 1 :
            buffer.update({"update": simplelog.getNow()})
            op_status = {"opcode": opcode, "rcode": self.__addIpv6ToDict(buffer)}
            return op_status
        
        else :
            op_status = {"opcode": -1, "rcode": self.__sendErrorOp()}
            return op_status
        
    def __checkIpMsg(self, msg:dict) -> int :
        name = msg.get("name")
        note = msg.get("note")
        ipv6 = msg.get("IPv6")

        if check_parameter.checkStr(name) != 0 :
            return -1
        if len(name) == 0 :
            return -1
        
        if check_parameter.checkStr(note) != 0 :
            return -1
        
        if check_parameter.checkStrIPv6(ipv6) != 0 :
            return -1
        return 0
    
    def __completed(self) :
        self.__comflag = True

    def getComFlag(self) :
        return self.__comflag
        
        
    def run(self) :
        if self.__verifyPcode() == -1 :
            self.__ssocket.close()
            self.__log_handle.fflush()
            return -1
        
        op_status = self.__Op()
        if op_status.get("rcode") != 0 :
            self.__log_handle.error( "[" + str(threading.get_native_id()) + "]" + json.dumps(op_status) + " {}:{}".format(self.__peerid, self.__peerport))
        else :
            self.__log_handle.info( "[" + str(threading.get_native_id()) + "]" + json.dumps(op_status) + " {}:{}".format(self.__peerid, self.__peerport))
        
        self.__ssocket.close()
        self.__log_handle.fflush()

        self.__completed()
        if (simplelog.getNowNs() % 5 == 0) or self.__errflag :
            if COND_LOCK.acquire(blocking= False) :

                    JOIN_COND.notify()
                    COND_LOCK.release()
        

        #print(op_status)
        #global REPROT_DICT
        #print(REPROT_DICT)
        #print("The dict len is {}.".format(len(REPROT_DICT)))
        return 0 
    
class JoinDemon(threading.Thread) :
    def __init__(self, loghandle) :
        super().__init__()
        self.__loghandle = loghandle

    def run(self) :
        COND_LOCK.acquire()
        while (True) :
            JOIN_COND.wait()
            queue_len = len(THRAED_QUEUE)
            index = 0
            self.__loghandle.info("demon: start join process, queue len is {}.".format(queue_len))
            #test code
            #print("demon: start join process, queue len is {}.".format(queue_len))
            while (index < queue_len) :
                if THRAED_QUEUE[index].getComFlag() :

                    THRAED_QUEUE[index].join()
                    self.__loghandle.info("demon: join queue index {} , {}.".format(index, THRAED_QUEUE[index]))
                    #test code 
                    #print("demon: join queue index {} , {}.".format(index, THRAED_QUEUE[index]))
                    del THRAED_QUEUE[index]
                    self.__loghandle.info("demon: join queue index {} completed.".format(index))
                    #test code 
                    #print("demon: join queue index {} completed.".format(index))
                    queue_len = queue_len - 1
                else :
                    index = index + 1

    
def atexit_save(savefile, log_handle) :
    global REPROT_DICT
    if len(REPROT_DICT) == 0 :
        log_handle.info("The report dict is null, no need save.")
        return 0

    try :
        save = open(savefile, "w+")
    except PermissionError :
        log_handle.error("Can't open save file, do not save.")
        return 0
    else :
        json.dump(REPROT_DICT, save)
        log_handle.info("Save completed.")
        return 0
    
def checkSaveInfo(info: dict) -> int :
        name = info.get("name")
        note = info.get("note")
        ipv6 = info.get("IPv6")
        time = info.get("update")

        if check_parameter.checkStr(name) != 0 :
            return -1
        if len(name) == 0 :
            return -1
        
        if check_parameter.checkStr(note) != 0 :
            return -1
        
        if check_parameter.checkStrIPv6(ipv6) != 0 :
            return -1
        
        if check_parameter.checkStr(time) != 0 :
            return -1
        return 0
            
            
     
if __name__ == '__main__' :
    main()




