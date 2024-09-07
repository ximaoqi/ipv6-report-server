# IPv6 report
## 一个使用python编写的简单的信息汇报服务器，以汇报IPv6信息为例
本程序将会读取客户端的IPv6地址信息，并汇报给指定的服务器。当然，也可以从指定的服务器中获取相关的地址信息。本项目主要是将客户端的IPv6地址汇报给指定的服务器，类似与DDNS。
“为什么不直接使用域名对IPv6地址进行解析？这样会更方便使用。”
因为不想直接将自己设备的IPv6地址随意暴露。

[TOC]

### 项目文件表
| 文件名  | 所属端 | 描述 | 备注|
|-|-|-|-|
|check_parameter.py|共用|模块用于参数检查，在report_ipv6_server.py、report_ipv6_client.py、get_ipv6_client.py使用||
|get_v6_address.py|共用|模块获取IP地址，在report_ipv6_client.py使用||
|simplelog.py |共用|日志框架，在report_ipv6_server.py、report_ipv6_client.py、get_ipv6_client.py使用| [项目地址](https://github.com/ximaoqi/simplelog)|
|report_ipv6_server.py|服务端|服务端程序||
|server_config.json|服务端|服务端配置文件||
|server.crt|服务端|服务端证书|自签发证书，仅供测试使用。自行部署时请自行签发新的自签发证书。|
|server.key|服务端|服务端秘钥|自签发证书，仅供测试使用。自行部署时请自行签发新的自签发证书。|
|report_ipv6_client.py|客户端|汇报客户端||
|get_ipv6_client.py|客户端|获取信息客户端||
|client_config.json|客户端|客户端配置文件||

### 编写及运行环境
客户端： python3.9+，支持Windows及Linux，但Linux下需安装net-tools，即ifconfig。
服务端： python3.9+，支持linux（Windows未测试）。

### 部署及使用
#### 服务端：
1、将simplelog.py、check_parameter.py、report_ipv6_server.py程序文件，server.crt、server.key配置文件及server_config.json配置文件放入同一目录。
2、linux下使用`chmod +x report_ipv6_server.py`为程序赋予执行权限；
3、linux下使用使用`./report_ipv6_server.py &`或`python3 report_ipv6_server.py &`即可运行；

#### 汇报客户端：
1、将simplelog.py、check_parameter.py、get_v6_address.py、report_ipv6_client.py程序文件及client_config.json配置文件放入同一目录；
2、linux下使用`chmod +x report_ipv6_client.py`为程序赋予执行权限；
3、在linux下使用`./report_ipv6_client.py`或`python3 report_ipv6_client.py`即可运行程序，完成一次信息汇报；在Windows下，确保正常安装了python3后，打开对应目录直接双击运行report_ipv6_client.py即可运行，完成一次信息汇报。
4、在Windows下，可通过设置计划任务，周期性的汇报信息；同样，在Linux下，可使用corntab实现周期性汇报。

#### 获取信息客户端
1、将simplelog.py、check_parameter.py、get_ipv6_client.py程序文件及client_config.json配置文件放入同一目录；
2、linux下使用`chmod +x get_ipv6_client.py`为程序赋予执行权限；
3、在linux下使用`./get_ipv6_client.py`或`python3 get_ipv6_client.py`即可运行程序，读取服务器中存储的信息并打印至终端窗口；Windows下，确保正常安装了python3后，打开对应目录直接双击运行get_ipv6_client.py，即可运行程序，读取服务器中存储的信息并打印至终端窗口；
以上是运行后打印示例：
```
  contxet = ssl.SSLContext(ssl.PROTOCOL_TLS)
{'IPv6': '240e:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx', 'name': 'test', 'note': 'test', 'update': '2024-08-07 06:40:01'}
Press enter key to close.
```

### 配置文件
#### 服务端
report_ipv6_server.py启动时将会读取server_config.json配置文件，文件内容示例如下：
```
{
    "pcode":"c065f22688219503a796b275b355ce87",
    "server":"10.0.0.100",
    "port":10000,
    "logfile": "report_ipv6_server.log",
    "savefile": "save.json",
    "crefile": "server.crt",
    "keyfile": "server.key",
    "listen": 60 ,
    "net_timeout" : 60
}
```
**pcode:** pin码，用于校验客户端身份，一致时才可进行上传信息或拉取信息操作；
**server：** 服务监听地址。
**port：** 服务监听端口。
**logfile：** 日志输出文件。
**savefile：** 信息保存文件，当程序终止时，会将当前已收到的信息保存至此文件。启动时也会尝试读取此文件的信息。
**crefile：** 证书文件。
**keyfile：** 秘钥文件。
**listen：** 服务端listen数量。
**net_timeout：** 网络超时限制，为60s。

#### 客户端
report_ipv6_client.py、get_ipv6_client.py启动时将会读取client_config.json配置文件，文件内容示例如下：

```
{
    "pcode":"c065f22688219503a796b275b355ce87",
    "server":"10.0.0.100",
    "port":10000,
    "name":"test",
    "note":"test",
    "reportlog": "report_ipv6.log",
    "getlog": "get_ipv6.log",
    "isp": "CHINATELECOM",
    "net_timeout" : 60
}
```
**pcode:** pin码，用于校验客户端身份，一致时才可进行上传信息或拉取信息操作；
**server:** 服务器地址。
**port：** 服务端口。
**name：** 上传信息时，用于标客户端身份。
**note：** 上传信息时，可以携带的注释。
**reportlog：** report_ipv6_client.py运行日志的路径。
**getlog：** get_ipv6_client.py运行日志的路径。
**isp：** 根据isp名称确定IPv6地址的前缀，可填："CHINATELECOM"、"CHINAMOBILE"、"CHINAUNICOM"，请根据客户端实际的isp填写。report_ipv6_client.py使用。
**net_timeout：** 网络超时限制，为60s。

### 一些备注：
1、如果你使用的不是自签发证书，可以将eport_ipv6_client.py、get_ipv6_client.py中的这行代码注释：
```
    #If you have a non self issued certificate, you can cancel the next code in the client for higher security
    contxet.verify_mode = ssl.CERT_NONE
```
客户端将会校验服务端的证书。

2、如果的isp不在"CHINATELECOM"、"CHINAMOBILE"、"CHINAUNICOM"之中，可以将其添加至get_v6_address.py中的isp列表：
```
# isp v6 prefix
ISP = {"CHINATELECOM":"240e:", "CHINAMOBILE":"2409:", "CHINAUNICOM":"2408:"}
```
并在client_config.json配置文件中的isp填写即可。