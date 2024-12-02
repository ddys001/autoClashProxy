def removeDuplicateNode(proxyPool):
    proxiesNames = []
    proxies = []
    for proxy in proxyPool:
        if(proxy['name'] not in proxiesNames):
            proxies.append(proxy)
            proxiesNames.append(proxy['name'])

    return proxies

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