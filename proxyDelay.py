import requests
import yaml

def getProxyDelay(proxyName):
    bTimeOut = True
    url = f"http://127.0.0.1:59319/proxies/{proxyName}/delay?timeout=3000&url=http:%2F%2Fwww.gstatic.com%2Fgenerate_204"
    header = {
                "Authorization": "Bearer f8db5010-566d-409e-b06e-3553c06123c8",
             }

    delay = eval(requests.get(url, headers=header).text)

    if("delay" in delay):
        delay = delay["delay"]
        bTimeOut = False
    elif("message" in delay):
        delay = delay["message"]
    else:
        assert(0)

    print(f"{proxyName}: {delay}")

    return bTimeOut

def teseAllProxy():
    passProxy=[]
    with open("fakeList.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        for proxy in allProxy:
            if(not getProxyDelay(proxy['name'])):
                passProxy.append(proxy)

    return passProxy

if __name__ == "__main__":
    passCount = 0
    proxyCount = 0
    with open("fakeList.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        for proxy in allProxy:
            passCount = passCount + (0 if getProxyDelay(proxy['name']) else 1)

    print(f"测试正常节点{passCount}/{len(allProxy)}")
