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