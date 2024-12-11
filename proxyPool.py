import requests
import yaml

import sys
sys.path.append('.')

from processProxy import *
from parserUrl import *
from autoPush import *
from createGroup import *
from createConfigYaml import *
from proxyDelay import *

downloadProxy = {
    'http':  'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

def downloadFile(index, url):
    print("开始下载{}：{}".format(index, url), end=" ", flush=True)
    file = None
    try:
        req = requests.get(url, proxies=downloadProxy)
        if (req.status_code == 200):
            print("下载成功", end=" ", flush=True)
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
    for index, url in enumerate(sources):
        download = downloadFile(index+1, url)
        if(download != None):
            try:
                file = yaml.load(download, Loader=yaml.FullLoader)
                proxyPool += file["proxies"] if file["proxies"] != None else []
                print("成功获得节点")
            except yaml.parser.ParserError:
                print("解析节点失败")

    print("原始获取节点数量:", len(proxyPool))
    proxies = removeNodes(proxyPool)
    print("删除不符合节点后，节点数量:", len(proxies))

    return proxies

sourcePath = "source.url"
defaultConfigPath = "default.config"

if(len(sys.argv) > 1):
    proxies = getProxyFromSource(sourcePath)
    if(len(proxies) > 0):
        creatFakeConfig(proxies, defaultConfigPath)
    else:
        print("未获取到有效节点，不生成fake config文件")
else:
    proxies = teseAllProxy()
    if(len(proxies) > 20):
        creatConfig(proxies, defaultConfigPath)
        pushListFile("list.yaml")
    else:
        print("获取的有效节点不足，不生成config文件")