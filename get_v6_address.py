import subprocess

# isp v6 prefix
ISP = {"CHINATELECOM":"240e:", "CHINAMOBILE":"2409:", "CHINAUNICOM":"2408:"}


# get ip address rawdata
def get_net_raw(os_type) :
    
    if os_type == 'Windows' :
        net_raw = subprocess.check_output("ipconfig") 
    elif os_type == 'Linux' :
        net_raw = subprocess.check_output("ifconfig")
    else :
        net_raw = -1

    return net_raw

#format v6 add to str
def format_v6_addr(net_info, isp_v6_head, os_type) :
    net_info = str(net_info)
    add_start = net_info.find(isp_v6_head)
    
    if os_type == 'Windows' :
        add_end = net_info[add_start:].find('\\r')

    elif os_type == 'Linux' :
        #get linux distribution version
        os_type = subprocess.check_output("uname -a", shell=True)

        os_type = str(os_type)

        #cut the address according to the distribution version
        if (os_type.find("Debian") != -1) :
            add_end = net_info[add_start:].find(' ')

        elif (os_type.find("OpenWrt") != -1) :
            add_start = net_info.find("wan")
            add_start = net_info[add_start:].find(isp_v6_head) + add_start
            add_end = net_info[add_start:].find('/')
        
        else :
            add_end = -1
    
    if add_end != -1 :
        net = net_info[add_start: add_start + add_end]
    
    else :
        net = -1

    return net

def get_v6net(os_type, isp_v6_head) :
    net_raw = get_net_raw(os_type)
    
    if net_raw == -1 :
        return -1
    
    net = format_v6_addr(net_raw, isp_v6_head, os_type)
    if net == -1 :
        return -1
    
    return net





