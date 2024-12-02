def removeDuplicateNode(proxyPool):
    checkLists = ["name", "server"]

    allProxy = proxyPool
    for item in checkLists:
        proxiesItem  = []
        proxies = []
        for proxy in allProxy:
            if(proxy[item] not in proxiesItem):
                proxies.append(proxy)
                proxiesItem.append(proxy[item])
        allProxy = proxies

    return allProxy

def removeNotSupportCipher(proxyPool):
    notSupportCipher = ['ss']
    proxies = []
    for proxy in proxyPool:
        if('cipher' in proxy and proxy['cipher'] not in notSupportCipher):
            proxies.append(proxy)

    return proxies

def removeNodes(proxyPool):
    proxies = removeDuplicateNode(proxyPool)
    proxies = removeNotSupportCipher(proxies)

    return proxies