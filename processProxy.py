from testProxy import *

def removeDuplicateNode(proxyPool): #删除重复节点
    checkLists = ["name", "server"]

    allProxy = proxyPool
    for item in checkLists:
        proxiesItem  = []
        proxies = []
        for proxy in allProxy:
            if(proxy[item] in proxiesItem):
                continue
            proxies.append(proxy)
            proxiesItem.append(proxy[item])
        allProxy = proxies

    print(f"after removeDuplicateNode, 剩余节点数量{len(allProxy)}")
    return allProxy

def removeNotSupportCipher(proxyPool): #删除cipher不符合条件的节点
    notSupportCipher = ['ss']
    proxies = []
    for proxy in proxyPool:
        if('cipher' in proxy and proxy['cipher'] in notSupportCipher):
            continue
        proxies.append(proxy)

    print(f"after removeNotSupportCipher, 剩余节点数量{len(proxies)}")
    return proxies

def removeNotSupportUUID(proxyPool): #删除uuid不符合条件的节点
    notSupportUUID = ['Free']
    proxies = []
    for proxy in proxyPool:
        if('uuid' in proxy and proxy['uuid'] in notSupportUUID):
            continue
        proxies.append(proxy)

    print(f"after removeNotSupportUUID, 剩余节点数量{len(proxies)}")
    return proxies

def removePingFailPorxy(proxyPool):
    print("开始测试节点的可连接性：")
    proxies = []
    for index, proxy in enumerate(proxyPool):
        host = proxy['server']
        port = proxy['port']
        if(pingTest(index+1, host) and connectPort(host, port)):
            proxies.append(proxy)

    print(f"after removePingFailPorxy, 剩余节点数量{len(proxies)}")
    return proxies

def removeNotSupportType(proxyPool): #删除type不符合条件的节点
    notSupportType = ['vless']
    proxies = []
    for proxy in proxyPool:
        if('type' in proxy and proxy['type'] in notSupportType):
            continue
        proxies.append(proxy)

    return proxies

def removeNodes(proxyPool):
    proxies = removeDuplicateNode(proxyPool)
    proxies = removeNotSupportCipher(proxies)
    proxies = removeNotSupportUUID(proxies)
    proxies = removeNotSupportType(proxies)
    #proxies = removePingFailPorxy(proxies)

    return proxies