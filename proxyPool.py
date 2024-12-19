import requests
import yaml
import argparse

import sys
sys.path.append('.')

from processProxy import *
from autoPush import *
from createConfigYaml import *

def downloadFile(index, url, httpProxy, httpsProxy):
    print("开始下载{}：{}".format(index, url), end=" ", flush=True)
    file = None
    try:
        downloadProxy = {
                            'http':  httpProxy,
                            'https': httpsProxy,
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

def getProxyFromSource(sourcePath, httpProxy, httpsProxy):
    proxyPool = []
    sources = parserSourceUrl(open(sourcePath, encoding='utf8').read().strip().splitlines())
    for index, url in enumerate(sources):
        download = downloadFile(index+1, url, httpProxy, httpsProxy)
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

parser = argparse.ArgumentParser()
parser.add_argument("--urlfile", type=str, default="source.url", help="指定下载clash订阅链接的文件")
parser.add_argument("--config", type=str, default="default.config", help="生成clash配置文件的模板文件")
parser.add_argument("--file", type=str, default="list.yaml", help="最终生成的clash配置文件")
parser.add_argument("--http", type=str, default="http://127.0.0.1:7890", help="指定http proxy")
parser.add_argument("--https", type=str, default="http://127.0.0.1:7890", help="指定https proxy")
parser.add_argument("--port", type=int, default=34885, help="指定clash web ui的prot")
parser.add_argument("--auth", type=str, default="d53df256-8f1b-4f9b-b730-6a4e947104b6", help="指定clash web ui的Authorization")
parser.add_argument("--min", type=int, default=10, help="生成clash配置文件所需要的最少节点数量.默认数值为10")
parser.add_argument("--max", type=int, default=50, help="延迟测试中通过测试的最大节点数量。超过这个数字后，将停止延迟测试。默认数值为50")
parser.add_argument("--timeout", type=int, default=3000, help="延迟测试运行的时间")
parser.add_argument("--testurl", type=str, default="https://www.youtube.com/generate_204", help="指定延迟测试使用的url")
parser.add_argument("--nopush", action='store_true', help="不将生成的clash配置文件上传至github")
parser.add_argument("--retry", type=int, default=5, help="推送至github失败后重试的次数。默认数值为5次")

createClash = parser.add_mutually_exclusive_group(required=True)
createClash.add_argument("--local", action='store_true', help="对--file指定文件进行处理后，生成延迟测试所需要的clash配置文件")
createClash.add_argument("--download", action='store_true', help="下载公开的订阅文件，在本地生成--file指定的延迟测试所需要的clash配置文件。")
createClash.add_argument("--delay", action='store_true', help="对指定的配置文件进行延迟测试，生成--file指定的配置文件。默认成功后会推送至github")
createClash.add_argument("--location", action='store_true', help="对--file指定文件节点按照地区分类后生成配置文件。默认成功后会推送至github")
createClash.add_argument("--onlypush", action='store_true', help="只推送提交至github")

args = parser.parse_args()

print(f"自动生成配置文件所需的最小节点数量为：{args.min}")
if(args.local): #处理指定的clash配置文件，删除里面不符合要求的节点，生成新的配置文件
    print(f"开始处理文件{args.file}，删除其中不符合要求的节点。")
    proxies = yaml.load(open(args.file, encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
    proxies = removeNodes(proxies)
    if(len(proxies) > args.min):
        creatTestConfig(proxies, args.config, args.file)
    else:
        print("有效节点数量不足，不生成clash配置文件")
elif(args.download): #根据urlfile文件中的订阅链接下载配置文件，删除里面不符合要求的节点，生成新的配置文件
    proxies = getProxyFromSource(args.urlfile, args.http, args.https)
    if(len(proxies) > args.min):
        creatTestConfig(proxies, args.config, args.file)
    else:
        print("有效节点数量不足，不生成clash配置文件")
elif(args.delay): #对配置文件中的节点进行延迟测试，删除延迟不符合要求的节点。
    print(f"延迟测试通过的最大节点数量：{args.max}")
    proxies = teseAllProxy(args.file, args.max, args.port, args.auth, args.timeout, args.testurl)
    if(len(proxies) > args.min):
        creatConfig(proxies, args.config, args.file, args.http, args.https)
        if(not args.nopush):
            pushFile(args.file, args.retry)
        else:
            print("指定不推送至github")
    else:
        print("有效节点数量不足，不生成clash配置文件")
elif(args.location):
    print("开始按照地区对节点进行分类。")
    proxies = yaml.load(open(args.file, encoding='utf8').read(), Loader=yaml.FullLoader)["proxies"]
    creatConfig(proxies, args.config, args.file, args.http, args.https)
    if(not args.nopush):
        pushFile(args.file, args.retry)
    else:
        print("指定不推送至github")
elif(args.onlypush):
    pushRepo(args.retry)
else:
    print("invalid parma")