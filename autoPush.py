import git

def pushListFile(listFile):
    repo = git.Repo(".")

    listStatus = repo.git.status(listFile)
    if ("modified" in listStatus):
        print("本地订阅文件已更新，开始推送至github。")
        repo.git.add(listFile)
        repo.git.commit("-m", "更新节点")
        try:
            repo.remotes.origin.push()
            print("订阅文件已在github上更新")
        except git.exc.GitCommandError:
            print("代码推送至github失败")
    else:
        print("本地订阅文件未更新，无需推送至github。")