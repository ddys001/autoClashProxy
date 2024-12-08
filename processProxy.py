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

    return allProxy

def removeNotSupportCipher(proxyPool): #删除cipher不符合条件的节点
    notSupportCipher = ['ss']
    proxies = []
    for proxy in proxyPool:
        if('cipher' in proxy and proxy['cipher'] in notSupportCipher):
            continue
        proxies.append(proxy)

    return proxies

def removeNotSupportUUID(proxyPool): #删除uuid不符合条件的节点
    notSupportUUID = ['Free']
    proxies = []
    for proxy in proxyPool:
        if('uuid' in proxy and proxy['uuid'] in notSupportUUID):
            continue
        proxies.append(proxy)

    return proxies

def removePingFailPorxy(proxyPool):
    proxies = []
    for proxy in proxyPool:
        host = proxy['server']
        port = proxy['port']
        if(pingTest(host) and connectPort(host, port)):
             proxies.append(proxy)

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
    proxies = removePingFailPorxy(proxies)

    return proxies