import requests
import random

import json
import time
import yaml

from potime import RunTime

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

def queryNDSInCFW(host, port=34885, Authorization="d53df256-8f1b-4f9b-b730-6a4e947104b6"):
    ip = "127.0.0.1"

    url = f"http://127.0.0.1:{port}/dns/query?name={host}"
    header = { "Authorization": f"Bearer {Authorization}"}
    message = requests.get(url, headers=header)
    if ("Answer" in message.text):
        answer = json.loads(message.text)["Answer"]
        for data in answer:
            if (data['type'] == 1):
                ip = data['data']
                break

    return ip

def loadConfigInCFW(configPath, retry, port=34885, Authorization="d53df256-8f1b-4f9b-b730-6a4e947104b6"):
    print(f"开始加载配置文件{configPath}。")
    url = f"http://127.0.0.1:{port}/configs"

    header = { "Authorization": f"Bearer {Authorization}"}
    param = {"force": "true"}
    body = {"path": configPath}

    bLoadSuccessful = False
    for i in range(retry):
        print(f"开始第{i + 1}次加载配置文件：", end="", flush=True)
        message = requests.put(url, headers=header, params=param, json=body)
        code = message.status_code

        if code == 204:
            print("配置文件加载成功")
            bLoadSuccessful = True
            break
        else:
            print(message.text)
            print("配置文件加载失败")
            time.sleep(2)

        if (i == (retry - 1)):
            print("达到最大重试次数，退出加载配置。")

    return bLoadSuccessful

def getProxyDelay(proxy, port, Authorization, timeout, testurl):
    proxyName = proxy['name']

    url = f"http://127.0.0.1:{port}/proxies/{proxyName}/delay"
    header = {"Authorization": f"Bearer {Authorization}"}
    param  = {"timeout": timeout, "url": testurl}

    delay = eval(requests.get(url, headers=header, params=param).text)

    if("delay" in delay):
        delay = delay["delay"]
    elif("message" in delay):
        delay = delay["message"]
        proxy = None
    else:
        assert(0)

    message = f"{proxyName}: {delay}"

    return (proxy, message)

@RunTime
def removeTimeoutProxy(proxies, port=34885, Authorization="d53df256-8f1b-4f9b-b730-6a4e947104b6", timeout=3000, testurl="https://www.youtube.com/generate_204"):
    passProxy=[]
    print(f"延迟测试超时时间为：{timeout}ms")
    print(f"延迟测试url为：{testurl}")
    print(f"测试节点总数为：{len(proxies)}")
    random.shuffle(proxies)
    try:
        with ThreadPoolExecutor(max_workers=15) as threadPool:
            allTask = [threadPool.submit(getProxyDelay, proxy, port, Authorization, timeout, testurl) for proxy in proxies]

            for index, future in enumerate(as_completed(allTask)):
                proxy, message = future.result()
                if (proxy != None):
                    passProxy.append(proxy)
                print(f"节点{index + 1}: {message}")
    except Exception as e:
        print(f"测试发生错误：{e}")

    print(f"测试正常节点: {len(passProxy)}/{len(proxies)}")

    return passProxy

if __name__ == "__main__":
    # configPath = f"{os.getcwd()}/list.yaml"
    # loadConfigInCFW(configPath, 5)
    # print(queryNDSInCFW("www.baidu.com"))

    proxies = yaml.load(open("list.yaml", encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
    removeTimeoutProxy(proxies)