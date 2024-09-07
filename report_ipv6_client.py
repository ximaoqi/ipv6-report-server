import socket
import ssl
import json
import platform

import check_parameter
import get_v6_address
import simplelog


def main() :
    #config file path
    CONFIG_FILE = "client_config.json"

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
    name = config.get("name")
    note = config.get("note")
    logfile = config.get("reportlog")
    isp = get_v6_address.ISP.get(config.get("isp"))
    timeout = config.get("net_timeout")

    #open log handle
    log = simplelog.LogHandle(logfile, time_stamp_flag=True)

    #check config parmeter
    if check_parameter.checkStrIPv4(server_ip) == -1 :
        log.critical("The server address is unavailable.")

    if check_parameter.checkPort(server_port) == -1 :
        log.critical("The server port is unavailable.")

    if check_parameter.checkStr(pcode) == -1 :
        log.critical("The Pcode is unavailable.")

    if check_parameter.checkStr(name) == -1 :
        log.critical("The name is unavailable.")

    if check_parameter.checkStr(isp) == -1 :
        log.critical("The isp is unavailable.")

    if check_parameter.checkUint32(timeout) == -1 :
        log.error("The timeout is unavailable, set default value is 60.")
        timeout = 60

    if check_parameter.checkStr(note) == -1 :
        log.error("The note is unavailable, set default value is null string.")
        note = ""
        

    #get os_type and localhost ipv6 address
    os_type = platform.system()
    net = get_v6_address.get_v6net(os_type, isp)
    if net == -1 :
        log.critical("Failed to obtain IPv6 address.")


    server_addr = (server_ip, server_port)
    #init and set ssl socket
    contxet = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #If you have a non self issued certificate, you can cancel the next code in the client for higher security
    contxet.verify_mode = ssl.CERT_NONE
    ss = contxet.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    ss.settimeout(timeout)

    log.info("Start connect server.")
    try :
        ss.connect(server_addr)
    except ConnectionRefusedError :
        log.critical("Failed to connection Server.")
    except TimeoutError :
        log.critical("Failed to connection Server.")
    except OSError:
        log.critical("Failed to connection Server.")

    log.info("Start verifing pcode")
    client_ss = ReportClient(ss)
    if client_ss.verifyPcode(pcode, name) != 0 :
        log.critical(client_ss.rinfo + " rcode :" + str(client_ss.rcode))

    if client_ss.reportInfo(net, name, note) != 0 :
        log.critical(client_ss.rinfo + " rcode :" + str(client_ss.rcode))

    log.info("Report completed.")
    client_ss.close()
    return 0


class ReportClient :
    def __init__(self, ssl_socket) :
        self.__ssl_socket = ssl_socket

    def close(self) :
        self.__ssl_socket.close()

    def verifyPcode(self, pcode:str, name:str) -> int :
        self.__ssl_socket.send(json.dumps({"pcode": pcode, "name": name}).encode())

        #rmsg = json.loads(self.__ssl_socket.recv().decode())
        rmsg = self.recvSecure()
        self.rcode = rmsg.get("rcode")
        if self.rcode != 0 :
            self.rinfo = rmsg.get("rinfo")
            return self.rcode
        else :
            return 0
    
    def reportInfo(self, net, name, note) -> int :
        self.__ssl_socket.send(json.dumps({"opcode": 1, "IPv6":net, "name":name, "note": note}).encode())

        #rmsg = json.loads(self.__ssl_socket.recv().decode())
        rmsg = self.recvSecure()
        self.rcode = rmsg.get("rcode") 
        if self.rcode != 0 :
            self.rinfo = rmsg.get("rinfo")
            return self.rcode
        else :
            return 0
        
    def getInfo(self, name) -> int:
        self.__ssl_socket.send(json.dumps({"opcode": 2, "name": name}).encode())
        #rmsg = json.loads(self.__ssl_socket.recv().decode())
        rmsg = self.recvSecure()
        if rmsg.pop("rcode") != 0 :
            return -1
        
        print("Name\t\t\tIPv6\t\t\tNote\t\t\tUpdate time")
        for i in rmsg :
            print("{}\t\t{}\t\t{}\t\t{}".format(i.get("name"), i.get("ipv6"), i.get("note"), i.get("update")))

        return 0 
    
    def recvSecure(self) :
        try :
            rmsg = json.loads(self.__ssl_socket.recv().decode())
        except TimeoutError:
            rmsg = {"rcode": "-1", "rinfo" : "Connection timeout."}
        except json.decoder.JSONDecodeError :
            rmsg = {"rcode": "-1", "rinfo" : "Connection loss."}

        return rmsg
        

if __name__ == '__main__' :
    main()
