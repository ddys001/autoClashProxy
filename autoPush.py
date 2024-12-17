import git

def pushRepo(retry): #将提交推送至github
    repo = git.Repo(".")
    for i in range(retry):
        print(f"开始第{i + 1}次推送：", end="", flush=True)
        try:
            repo.remotes.origin.push()
            print("推送成功。")
            break
        except git.exc.GitCommandError:
            print("推送失败。", end="", flush=True)

        if(i < (retry - 1)):
            print("准备重新推送。")
        else:
            print("达到最大重试次数，退出推送。")

def pushFile(file, retry): #检查文件是否有修改，如果有修改，则将修改推送至github
    repo = git.Repo(".")

    listStatus = repo.git.status(file)
    if ("modified" in listStatus):
        print(f"{file}已更新，开始推送至github。")
        repo.git.add(file)
        repo.git.commit("-m", f"更新{file}")
        pushRepo(retry)
    else:
        print(f"{file}未更新，无需推送至github。")