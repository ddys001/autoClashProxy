import requests
import yaml

import sys
sys.path.append('.')

from processProxy import *
from parserUrl import *

downloadProxy = {
    'http':  'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

def downloadFile(url):
    print("开始下载：{}".format(url), end=" ", flush=True)
    file = None
    try:
        req = requests.get(url, proxies=downloadProxy)
        if (req.status_code == 200):
            print("下载成功")
            file =  req.content
        else:
            print("下载失败")
    except requests.exceptions.SSLError:
        print("SSLError 下载失败")
    except requests.exceptions.MissingSchema:
        print("Invalid URL: url")
    except requests.exceptions.ConnectionError:
        print("Connection aborted")

    return file

def getProxyFromSource(sourcePath):
    proxyPool = []
    sources = parserSourceUrl(open(sourcePath, encoding='utf8').read().strip().splitlines())
    for url in sources:
        download = downloadFile(url)
        if(download != None):
            file = yaml.load(download, Loader=yaml.FullLoader)
            proxyPool += file["proxies"] if file["proxies"] != None else []

    print("原始获取节点数量:", len(proxyPool))
    proxies = removeNodes(proxyPool)
    print("删除不符合节点后，节点数量:", len(proxies))

    return proxies

def creatConfig(proxyPool, defaultFile):
    defaultConfig = open(defaultFile, encoding='utf8').read()
    config = yaml.load(defaultConfig, Loader=yaml.FullLoader)

    proxiesNames = [proxy['name'] for proxy in proxies]

    config['proxies'] = proxies if config['proxies'] == None else config['proxies'] + proxies
    for group in config['proxy-groups']:
        group['proxies'] = proxiesNames if group['proxies'] == None else group['proxies'] + proxiesNames

    with open('list.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True)

    print("生成clash订阅文件：list.yaml")

sourcePath = "source.url"
defaultConfigPath = "default.config"
proxies = getProxyFromSource(sourcePath)

if(len(proxies) > 0):
    creatConfig(proxies, defaultConfigPath)
else:
    print("未获取到有效节点，不生成clash订阅文件")