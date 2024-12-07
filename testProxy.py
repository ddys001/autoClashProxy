import ping3
import socket

def pingTest(proxy):
    pingPass = False
    try:
        response_time = ping3.ping(proxy)
        if response_time is not None:
            print("Ping测试结果：{} 的平均响应时间为 {:.2f}ms".format(proxy, response_time), end = ", ", flush = True)
            pingPass = True
        else:
            print("Ping测试结果：{} 无法到达或超时".format(proxy))
    except Exception as e:
        print("节点无法连接")

    return pingPass

def connectPort(host, port):
    bOpen = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            bOpen = True
    except Exception as e:
        pass
    finally:
        sock.close()

    print("Port {} is {}.".format(port, "open" if(bOpen) else "close"))

    return bOpen
