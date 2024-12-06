import ping3
import yaml

def pingTest(proxy):
    pingPass = False
    try:
        response_time = ping3.ping(proxy)
        if response_time is not None:
            print("Ping测试结果：{} 的平均响应时间为 {:.2f}ms".format(proxy, response_time))
            pingPass = True
        else:
            print("Ping测试结果：{} 无法到达或超时".format(proxy))
    except ping3.exceptions.PingError:
        print("节点无法连接")

    return pingPass

Count=0
with open("list.yaml", encoding='utf8') as fp:
    listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
    for proxy in listFile['proxies']:
        if(pingTest(proxy["server"]) == True):
            Count += 1
    print("pass count:", Count)
