import requests
import random

import os
import time

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
            if(item in proxy and proxy[item] in notSupportItems[item]):
                continue
            proxies.append(proxy)
        proxyPool = proxies
        print(f"after removeNotSupport_{item}, 剩余节点数量{len(proxies)}")

    return proxies

def removeNodes(proxyPool):
    proxies = removeDuplicateNode(proxyPool)
    proxies = removeNotSupportNode(proxies)

    return proxies

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

def getProxyDelay(index, proxyName, port, Authorization, timeout, testurl):
    bPassTest = False

    url = f"http://127.0.0.1:{port}/proxies/{proxyName}/delay"
    header = {
                "Authorization": f"Bearer {Authorization}",
             }

    param = {
                "timeout": timeout,
                "url": testurl
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

def removeTimeoutProxy(proxies, maxProxy, port=34885, Authorization="d53df256-8f1b-4f9b-b730-6a4e947104b6", timeout=3000, testurl="https://www.youtube.com/generate_204"):
    passProxy=[]
    print(f"延迟测试超时时间为：{timeout}")
    print(f"延迟测试url为：{testurl}")
    print(f"测试节点总数为：{len(proxies)}")
    random.shuffle(proxies)
    try:
        for index, proxy in enumerate(proxies):
            if(getProxyDelay(index+1, proxy['name'], port, Authorization, timeout, testurl)):
                passProxy.append(proxy)

            if(((index + 1) % 30) == 0):
                print(f"测试正常节点: {len(passProxy)}/{index + 1}")

            if(len(passProxy) == maxProxy): #获得有效的的节点数已经足够多 退出测试
                print("获得预期最大节点数量，退出延迟测试。")
                break
    except KeyboardInterrupt:
        print("取消测试，延迟测试结束。")
    except Exception as e:
        print(f"发生错误：{e}。延迟测试结束。")

    print(f"测试正常节点: {len(passProxy)}/{len(proxies)}")

    return passProxy

if __name__ == "__main__":
    configPath = f"{os.getcwd()}/list.yaml"
    loadConfigInCFW(configPath, 5)