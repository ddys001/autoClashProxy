import requests
import yaml

import sys
sys.path.append('.')

from processProxy import *
from autoPush import *
from createConfigYaml import *

def downloadFile(index, url):
    print("开始下载{}：{}".format(index, url), end=" ", flush=True)
    file = None
    try:
        downloadProxy = {
                            'http':  'http://127.0.0.1:7890',
                            'https': 'http://127.0.0.1:7890',
                        }

        req = requests.get(url, proxies=downloadProxy)
        if (req.status_code == 200):
            print("下载成功", end=" ", flush=True)
            file =  req.text.replace("!<str> ", "")
        else:
            print("下载失败")
    except requests.exceptions.SSLError:
        print("SSLError 下载失败")
    except requests.exceptions.MissingSchema:
        print("Invalid URL: url")
    except requests.exceptions.ConnectionError:
        print("Connection aborted")

    return file

def parserSourceUrl(sourceFile):
    print("解析到以下有效的url:")
    allUrl = []
    for url in sourceFile:
        if (url.strip().startswith("#") or url.strip().startswith("//")): #删除注释
            continue
        if (url.isspace() or len(url) == 0): #删除空行
            continue
        if(url not in allUrl): #删除重复url
            allUrl.append(url)
            print(url)

    print("解析完成，共获得{}个有效url".format(len(allUrl)))
    return allUrl

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
            except Exception as e:
                print(f"解析节点失败。 Error：{e}")

    print("原始获取节点数量:", len(proxyPool))
    proxies = removeNodes(proxyPool)
    print("删除不符合节点后，节点数量:", len(proxies))

    return proxies

sourcePath = "source.url"
defaultConfigPath = "default.config"
configFile = "list.yaml"

minProxy = 20
if(len(sys.argv) == 2 and sys.argv[1] == "-f"): #第一次生成config文件，里面包含所有从网上获取的节点
    proxies = getProxyFromSource(sourcePath)
    if(len(proxies) > minProxy):
        creatTestConfig(proxies, defaultConfigPath, configFile)
    else:
        print("未获取到有效节点，不生成config文件")
elif(len(sys.argv) == 2 and sys.argv[1] == "-d"): #第二次生成config文件，删除延迟不符合要求的节点。并将文件上传至github
    proxies = teseAllProxy(configFile)
    if(len(proxies) > minProxy):
        creatConfig(proxies, defaultConfigPath, configFile)
        pushListFile(configFile)
    else:
        print("获取的有效节点不足，不生成config文件")
else:
    print("invalid parma")