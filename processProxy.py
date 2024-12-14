import requests
import yaml

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

def removeNotSupportType(proxyPool): #删除type不符合条件的节点
    notSupportType = ['vless']
    proxies = []
    for proxy in proxyPool:
        if('type' in proxy and proxy['type'] in notSupportType):
            continue
        proxies.append(proxy)

    print(f"after removeNotSupportType, 剩余节点数量{len(proxies)}")

    return proxies

def removeNodes(proxyPool):
    proxies = removeDuplicateNode(proxyPool)
    proxies = removeNotSupportCipher(proxies)
    proxies = removeNotSupportUUID(proxies)
    proxies = removeNotSupportType(proxies)

    return proxies

def getProxyDelay(index, proxyName):
    bPassTest = False

    port = 34885
    Authorization = "d53df256-8f1b-4f9b-b730-6a4e947104b6"
    url = f"http://127.0.0.1:{port}/proxies/{proxyName}/delay"
    header = {
                "Authorization": f"Bearer {Authorization}",
             }

    param = {
                "timeout": "3000",
                "url": "https://www.youtube.com/generate_204"
            }

    delay = eval(requests.get(url, headers=header, params=param).text)

    if("delay" in delay):
        delay = delay["delay"]
        bPassTest = True
    elif("message" in delay):
        delay = delay["message"]
    else:
        assert(0)

    print(f"节点{index}: {proxyName}: {delay}")

    return bPassTest

def teseAllProxy(configFile):
    passProxy=[]
    with open(configFile, encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        print(f"测试节点总数为：{len(allProxy)}")
        for index, proxy in enumerate(allProxy):
            if(getProxyDelay(index+1, proxy['name'])):
                passProxy.append(proxy)

            if(((index + 1) % 30) == 0):
                print(f"测试正常节点: {len(passProxy)}/{index + 1}")

        print(f"测试正常节点: {len(passProxy)}/{len(allProxy)}")

    return passProxy

if __name__ == "__main__":
    teseAllProxy("list.yaml")