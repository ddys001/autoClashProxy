import requests
import yaml
import argparse

import os
from potime import RunTime
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.append('.')

from processProxy import *
from autoPush import *
from createConfigYaml import *

def downloadProxy(url, httpProxy, httpsProxy):
    print(f"开始下载：{url}")
    download = None
    try:
        downloadProxy = {'http':  httpProxy, 'https': httpsProxy}

        req = requests.get(url, proxies=downloadProxy)
        if (req.status_code == 200):
            print(f"{url}下载成功")
            download =  req.text.replace("!<str> ", "")
        else:
            print(f"{url}下载失败")
    except requests.exceptions.SSLError:
        print(f"{url}：SSLError 下载失败")
    except requests.exceptions.MissingSchema:
        print(f"{url}：Invalid URL")
    except requests.exceptions.ConnectionError:
        print(f"{url}：Connection aborted")

    proxies = []
    if (download != None):
        try:
            file = yaml.load(download, Loader=yaml.FullLoader)
            proxies = file["proxies"] if file["proxies"] != None else []
            print(f"{url}：成功获得节点")
        except Exception as e:
            print(f"{url}：解析节点失败。 Error：{e}")

    return proxies

def parserSourceUrl(sourceFile):
    print(f"从{sourceFile}解析出以下有效的url:")
    allUrls = open(sourceFile, encoding='utf8').read().strip().splitlines()
    allUrl = []
    for url in allUrls:
        if (url.strip().startswith("#") or url.strip().startswith("//")): #删除注释
            continue
        if (url.isspace() or len(url) == 0): #删除空行
            continue
        if(url not in allUrl): #删除重复url
            allUrl.append(url)
            print(url)

    print("解析完成，共获得{}个有效url".format(len(allUrl)))
    return allUrl

@RunTime
def getProxyFromSource(sourcePath, httpProxy, httpsProxy):
    proxyPool = []
    sources = parserSourceUrl(sourcePath)
    with ThreadPoolExecutor(max_workers=15) as threadPool:
        allTask = [threadPool.submit(downloadProxy, url, httpProxy, httpsProxy) for url in sources]

        for future in as_completed(allTask):
            proxyPool += future.result()

    print("下载完成")
    print("获取节点数量:", len(proxyPool))

    return proxyPool

parser = argparse.ArgumentParser()
parser.add_argument("--urlfile", type=str, default="source.url", help="指定下载clash订阅链接的文件")
parser.add_argument("--config", type=str, default="default.config", help="生成clash配置文件的模板文件")
parser.add_argument("--file", type=str, default="list.yaml", help="最终生成的clash配置文件")
parser.add_argument("--http", type=str, default="http://127.0.0.1:7890", help="指定http proxy")
parser.add_argument("--https", type=str, default="http://127.0.0.1:7890", help="指定https proxy")
parser.add_argument("--port", type=int, default=34885, help="指定clash web ui的prot")
parser.add_argument("--auth", type=str, default="d53df256-8f1b-4f9b-b730-6a4e947104b6", help="指定clash web ui的Authorization")
parser.add_argument("--min", type=int, default=10, help="生成clash配置文件所需要的最少节点数量。默认数值为10")
parser.add_argument("--timeout", type=int, default=2000, help="延迟测试运行的时间，默认超时时间为2000ms")
parser.add_argument("--testurl", type=str, default="https://www.youtube.com/generate_204", help="指定延迟测试使用的url")
parser.add_argument("--push", action='store_true', help="将生成的clash配置文件上传至github")
parser.add_argument("--retry", type=int, default=5, help="推送至github失败后重试的次数。默认数值为5次")
parser.add_argument("--noDownload", action='store_true', help="不下载公开节点，使用本地配置文件")

createClash = parser.add_mutually_exclusive_group(required=True)
createClash.add_argument("--local", action='store_true', help="对--file指定文件进行处理后，生成延迟测试所需要的clash配置文件")
createClash.add_argument("--download", action='store_true', help="下载公开的订阅文件，在本地生成--file指定的延迟测试所需要的clash配置文件。")
createClash.add_argument("--update", action='store_true', help="更新配置文件，并将其推送至github")

args = parser.parse_args()
bNoDownload = args.noDownload
proxies = None
configPath = f"{os.getcwd()}/{args.file}"

if (args.local): #处理指定的clash配置文件，删除里面不符合要求的节点，生成新的配置文件
    print(f"开始处理配置文件：{args.file}。")
    proxies = yaml.load(open(args.file, encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
    proxies = processNodes(proxies)
    bNoDownload = False

if ((args.download or args.update) and (not bNoDownload)): #根据urlfile文件中的订阅链接下载配置文件，删除里面不符合要求的节点，生成新的配置文件
    print("开始下载公开节点。")
    proxies = getProxyFromSource(args.urlfile, args.http, args.https)

if (bNoDownload):
    print("不下载公开节点，使用本地配置文件。")
    proxies = yaml.load(open(args.file, encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
    bSuccess = True
else:
    bSuccess = creatConfig(proxies, args.min, args.config, args.file, args.http, args.https)

if (args.update): #对配置文件中的节点进行延迟测试，删除延迟不符合要求的节点。
    if (bSuccess and loadConfigInCFW(configPath, args.retry)):
        bSuccess = False
        proxies = yaml.load(open(args.file, encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
        proxies = removeTimeoutProxy(proxies, args.port, args.auth, args.timeout, args.testurl)
        bSuccess = creatConfig(proxies, args.min, args.config, args.file, args.http, args.https)
        if (bSuccess):
            loadConfigInCFW(configPath, args.retry) #延迟测试结束，加载最终生成的配置文件
    else:
        bSuccess = False

    if (not bSuccess):
        print("配置文件更新失败")

if (bSuccess and args.push):
    pushFile(args.file, args.retry)