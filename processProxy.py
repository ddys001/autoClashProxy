import requests
import yaml

from concurrent.futures import ThreadPoolExecutor, as_completed

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

        print(f"after removeDuplicate_{item}, 剩余节点数量{len(allProxy)}")

    return allProxy

def removeNotSupportNode(proxyPool): #删除clash不支持的节点
    notSupportItems = {
        "cipher" : ['ss', "chacha20-poly1305"],
        "uuid"   : ['Free'],
        "type"   : ['vless', 'hysteria', 'hysteria2']
    }

    for item in notSupportItems.keys():
        proxies = []
        for proxy in proxyPool:
            if (item in proxy and proxy[item] in notSupportItems[item]):
                continue
            proxies.append(proxy)
        proxyPool = proxies
        print(f"after removeNotSupport_{item}, 剩余节点数量{len(proxies)}")

    return proxies

#TLS must be true with h2/grpc network in vmess
def setTLSForVmess(proxyPool):
    proxies = []
    for proxy in proxyPool:
        if (proxy['type'] == "vmess" and "network" in proxy):
            if (proxy['network'] in ["grpc"]):
                proxy['tls'] = True
        proxies.append(proxy)

    return proxies

def processNodes(proxyPool):
    proxies = removeDuplicateNode(proxyPool)
    proxies = removeNotSupportNode(proxies)
    proxies = setTLSForVmess(proxies)

    return proxies

def removeTimeoutProxy(proxies, profile):
    passProxy=[]
    print(f"延迟测试超时时间为：{profile.clash.timeout}ms")
    print(f"延迟测试url为：{profile.clash.delayUrl}")
    print(f"测试节点总数为：{len(proxies)}")
    try:
        with ThreadPoolExecutor(max_workers=15) as threadPool:
            allTask = [threadPool.submit(profile.clash.queryProxyDelay, proxy) for proxy in proxies]

            for index, future in enumerate(as_completed(allTask)):
                proxy, message = future.result()
                if (proxy != None):
                    passProxy.append(proxy)
                print(f"节点{index + 1}: {message}")
    except Exception as e:
        print(f"测试发生错误：{e}")

    print(f"测试正常节点: {len(passProxy)}/{len(proxies)}")

    return passProxy

def downloadProxy(url, requestsProxy):
    print(f"开始下载：{url}")
    download = None
    try:
        req = requests.get(url, proxies=requestsProxy)
        if (req.status_code == 200):
            print(f"{url} 下载完成")
            download =  req.text
        else:
            print(f"{url} 下载失败")
    except Exception as e:
        print(f"{url}：{e}")

    proxies = []
    if (download != None):
        download = download.replace("!<str> ", "")
        try:
            file = yaml.load(download, Loader=yaml.FullLoader)
            proxies = file["proxies"] if file["proxies"] != None else []
            print(f"{url}：成功获得节点")
        except Exception as e:
            print(f"{url}：解析节点失败。 Error：{e}")

    return (proxies, url)

def getProxyFromSource(sources, requestsProxy):
    proxyPool = []
    with ThreadPoolExecutor(max_workers=15) as threadPool:
        allTask = [threadPool.submit(downloadProxy, url, requestsProxy) for url in sources]

        for index, future in enumerate(as_completed(allTask)):
            proxies, url = future.result()
            proxyPool += proxies
            print(f"{index + 1}、{url} 处理完成")

    print("全部链接下载完成")
    print("获取节点数量:", len(proxyPool))

    return proxyPool

if __name__ == "__main__":
    pass