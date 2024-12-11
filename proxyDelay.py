import requests
import yaml

def getProxyDelay(index, proxyName):
    bPassTest = False
    url = f"http://127.0.0.1:59319/proxies/{proxyName}/delay?timeout=3000&url=http:%2F%2Fwww.gstatic.com%2Fgenerate_204"
    header = {
                "Authorization": "Bearer f8db5010-566d-409e-b06e-3553c06123c8",
             }

    delay = eval(requests.get(url, headers=header).text)

    if("delay" in delay):
        delay = delay["delay"]
        bPassTest = True
    elif("message" in delay):
        delay = delay["message"]
    else:
        assert(0)

    print(f"节点{index}: {proxyName}: {delay}")

    return bPassTest

def teseAllProxy():
    passProxy=[]
    with open("fakeList.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        print(f"测试节点总数为：{len(allProxy)}")
        for index, proxy in enumerate(allProxy):
            if(getProxyDelay(index+1, proxy['name'])):
                passProxy.append(proxy)

        print(f"测试正常节点: {len(passProxy)}/{len(allProxy)}")

    return passProxy

if __name__ == "__main__":
    passCount = 0
    proxyCount = 0
    with open("fakeList.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        for index, proxy in enumerate(allProxy):
            passCount = passCount + (1 if getProxyDelay(index+1, proxy['name']) else 0)

    print(f"测试正常节点{passCount}/{len(allProxy)}")
