import requests
import yaml

def getProxyDelay(index, proxyName):
    bPassTest = False

    port = 52039
    url = f"http://127.0.0.1:{port}/proxies/{proxyName}/delay"
    header = {
                "Authorization": "Bearer f8db5010-566d-409e-b06e-3553c06123c8",
             }

    param = {
                "timeout": "3000",
                "url": "http://www.gstatic.com/generate_20"
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

def teseAllProxy():
    passProxy=[]
    with open("fakeList.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        allProxy = listFile['proxies']
        print(f"测试节点总数为：{len(allProxy)}")
        for index, proxy in enumerate(allProxy):
            if(getProxyDelay(index+1, proxy['name'])):
                passProxy.append(proxy)

            if(index % 30 == 0):
                print(f"测试正常节点: {len(passProxy)}/{len(allProxy)}")

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
