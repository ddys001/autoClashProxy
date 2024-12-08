import requests
import socket
import yaml
import json

httpProxy = {
    'http':  'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

def getPorxyCountry(proxy):
    country = "未知地区"
    try:
        ip = socket.gethostbyname(proxy['server'])
        data = requests.get(f"http://demo.ip-api.com/json/{ip}?fields=66842623&lang=zh-CN", proxies=httpProxy).text
        if(len(data) != 0):
            data = json.loads(data)
            country = data['country'] if (data['status'] == "success") else "未知地区"
    except Exception as e:
        print(e)

    print(f"{proxy['server']} {country}")
    return country

def createGroup(name, groupType, proxies):
    group = {
        "name"     : name,
        "type"     : groupType,
        "proxies"  : proxies,
    }

    if(groupType == "load-balance"):
        group['url'] = "https://www.google.com/favicon.ico"
        group["interval"] = 300

    return group

def createLocationProxyGroup(proxies):
    print("按照ip地址查询节点所属地区")

    location = dict()
    for proxy in proxies:
        country = getPorxyCountry(proxy)
        countryGroup = location[country] if (country in location) else createGroup(country, "load-balance", [])
        countryGroup['proxies'].append(proxy['name'])

        location[country] = countryGroup

    return location

if __name__ == "__main__":
    with open("list.yaml", encoding='utf8') as fp:
        listFile = yaml.load(fp.read(), Loader=yaml.FullLoader)
        createLocationProxyGroup(listFile['proxies'])