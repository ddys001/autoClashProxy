import requests
import yaml

downloadProxy = {
'http': '127.0.0.1:7890',
'https': '127.0.0.1:7890',
}

def downloadFile(url):
    print("开始下载：{}".format(url), end=" ")
    file = requests.get(url, proxies=downloadProxy)
    if (file.status_code == 200):
        print("下载成功")
        return file.content
    else:
        print("下载失败")
        return None

def getProxyFromSource(sourcePath):
    proxyPool = []
    sources = open(sourcePath, encoding='utf8').read().strip().splitlines()
    for url in sources:
        download = downloadFile(url)
        if(download != None):
            file = yaml.load(download, Loader=yaml.FullLoader)
            proxyPool += file["proxies"]

    return proxyPool

def creatConfig(proxies, defaultFile):
    proxyCount = len(proxies)

    if(proxyCount == 0):
        return
    else:
        print("proxy count:", proxyCount)

    defaultConfig = open(defaultFile, encoding='utf8').read()
    config = yaml.load(defaultConfig, Loader=yaml.FullLoader)

    proxiesNames = [proxy['name'] for proxy in proxies]

    config['proxies'] = proxies if config['proxies'] == None else config['proxies'] + proxies
    for group in config['proxy-groups']:
        group['proxies'] = proxiesNames if group['proxies'] == None else group['proxies'] + proxiesNames

    with open('list.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True)

sourcePath = "source.url"
defaultConfigPath = "default.config"
proxies = getProxyFromSource(sourcePath)
creatConfig(proxies, defaultConfigPath)