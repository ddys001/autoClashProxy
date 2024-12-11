import yaml
from createGroup import *

listFile = "list.yaml"
fakeConfig = "fakeList.yaml"

def creatConfig(proxies, defaultFile):
    defaultConfig = open(defaultFile, encoding='utf8').read()
    config = yaml.load(defaultConfig, Loader=yaml.FullLoader)

    proxiesNames = [proxy['name'] for proxy in proxies]

    config['proxies'] = proxies if config['proxies'] == None else config['proxies'] + proxies

    config['proxy-groups'] = []
    config['proxy-groups'].append(createGroup("proxinode", "select", ["选择地区", "自动选择", "手动选择"]))
    config['proxy-groups'].append(createGroup("自动选择", "load-balance", proxiesNames))

    selectCountry = createGroup("选择地区", "select", [])

    countryGroup = createLocationProxyGroup(proxies)
    allCountry = []
    for country in countryGroup:
        selectCountry['proxies'].append(country)
        allCountry.append(countryGroup[country])

    config['proxy-groups'].append(selectCountry)
    config['proxy-groups'].append(createGroup("手动选择", "select", proxiesNames))

    config['proxy-groups'] += allCountry

    with open(listFile, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True)

    print("生成clash订阅文件：{}".format(listFile))

def creatFakeConfig(proxies, defaultFile):
    defaultConfig = open(defaultFile, encoding='utf8').read()
    config = yaml.load(defaultConfig, Loader=yaml.FullLoader)

    proxiesNames = [proxy['name'] for proxy in proxies]

    config['proxies'] = proxies if config['proxies'] == None else config['proxies'] + proxies

    config['proxy-groups'] = [createGroup("proxinode", "select", proxiesNames)]

    with open(fakeConfig, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True)

    print("生成clash订阅文件：{}".format(fakeConfig))