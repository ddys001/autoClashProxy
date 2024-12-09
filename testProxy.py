import ping3
import socket
import yaml

def pingTest(index, proxy):
    print(f"测试节点{index}：", end = "", flush = True)
    pingPass = False
    try:
        response_time = ping3.ping(proxy)
        if response_time is not None:
            print("{} 的平均响应时间为 {:.2f}ms".format(proxy, response_time), end = ", ", flush = True)
            pingPass = True
    except Exception as e:
        pass
    finally:
        if(pingPass == False):
            print(f"{proxy}无法连接")

    return pingPass

def connectPort(host, port):
    bOpen = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        if result == 0:
            bOpen = True
    except Exception as e:
        print(e, end = ", ", flush = True)
    finally:
        sock.close()

    print("Port {} is {}.".format(port, "open" if(bOpen) else "close"))

    return bOpen

if __name__ == "__main__":
    passCount=0
    with open("list.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        for index, proxy in enumerate(listFile['proxies']):
            if(pingTest(index+1, proxy["server"]) and connectPort(proxy["server"], proxy["port"])):
                passCount += 1
        print("pass count: {}/{}".format(passCount, len(listFile['proxies'])))
