import subprocess
import sys
import os
import json
import re

def check_git_installed():
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def has_git_repo():
    git_dir = os.path.join(os.getcwd(), ".git")
    return os.path.exists(git_dir) and os.path.isdir(git_dir)

def read_hubconfig():
    hubconfig_path = os.path.join(os.getcwd(), ".hubconfig")
    if os.path.exists(hubconfig_path):
        try:
            with open(hubconfig_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("仓库URL")
        except json.JSONDecodeError:
            print("\033[91m.hubconfig文件格式错误\033[0m")
            return None
    return None

def validate_repo_url(url):
    patterns = [
        r'^https?://[\w.-]+/[\w.-]+/[\w.-]+\.git$',
        r'^git@[\w.-]+:[\w.-]+/[\w.-]+\.git$'
    ]
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False

def save_hubconfig(repo_url):
    hubconfig_path = os.path.join(os.getcwd(), ".hubconfig")
    config = {"仓库URL": repo_url}
    try:
        with open(hubconfig_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(".hubconfig文件已更新")
    except Exception as e:
        print(f"\033[91m保存.hubconfig失败: {e}\033[0m")

def update_gitignore():
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    
    ext = ".exe" if sys.platform.startswith("win") else ""
    
    ignore_entries = [
        ".gitignore", 
        ".hubconfig", 
        f"PushToHub{ext}", 
        f"InitHub{ext}", 
        f"Rollback{ext}", 
        f"DeleteHub{ext}"
    ]
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        added_entries = []
        for entry in ignore_entries:
            if entry not in content:
                content += f"\n{entry}"
                added_entries.append(entry)
        if added_entries:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f".gitignore已更新，添加了: {', '.join(added_entries)}")
        else:
            print(".gitignore中已存在所有需要忽略的文件")
    else:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(ignore_entries) + "\n")
        print("已创建.gitignore并添加所有需要忽略的文件")

def main():
    if not check_git_installed():
        print("\033[91m未安装git工具\033[0m")
        sys.exit(1)
    
    print("git工具已安装")
    
    if has_git_repo():
        print("当前目录已存在.git仓库")
    else:
        print("当前目录未初始化git仓库，执行git init...")
        try:
            result = subprocess.run(
                ["git", "init"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            print("git仓库初始化成功")
            update_gitignore()
        except subprocess.CalledProcessError as e:
            print(f"\033[91mgit init失败: {e.stderr}\033[0m")
            sys.exit(1)
    
    repo_url = read_hubconfig()
    if repo_url:
        print(f"检测到仓库URL: {repo_url}")
        if not validate_repo_url(repo_url):
            print("\033[91m.hubconfig中的仓库URL格式不正确\033[0m")
            repo_url = None
    
    if not repo_url:
        while True:
            repo_url = input("请输入远程仓库URL: ").strip()
            if not repo_url:
                print("\033[91m仓库URL不能为空，请重新输入\033[0m")
                continue
            if not validate_repo_url(repo_url):
                print("\033[91m仓库URL格式不正确，请重新输入\033[0m")
                continue
            break
        save_hubconfig(repo_url)
    
    try:
        result = subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("远程仓库已设置")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m设置远程仓库失败: {e.stderr}\033[0m")
        sys.exit(1)
    
    def get_current_branch():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            return result.stdout.strip()
        except:
            return "main"
    
    while True:
        pull_choice = input("是否拉取远程仓库内容? (y/n): ").strip().lower()
        if pull_choice in ['y', 'yes']:
            current_branch = get_current_branch()
            branch = input(f"请输入要拉取的分支名 (默认: {current_branch}): ").strip()
            if not branch:
                branch = current_branch
            
            print(f"正在拉取远程仓库 {branch} 分支内容...")
            try:
                result = subprocess.run(
                    ["git", "pull", "origin", branch],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=True
                )
                print("远程仓库内容拉取成功")
                break
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() or e.stdout.strip()
                print(f"\033[91m拉取失败: {error_msg}\033[0m")
                if "would be overwritten by merge" in error_msg:
                    print("\033[93m提示：本地存在未追踪的文件会被覆盖\033[0m")
                    print("请手动处理冲突文件后再拉取，或运行以下命令:")
                    print(f"  git stash")
                    print(f"  git pull origin {branch}")
                    print("  git stash pop")
                elif "not found in upstream" in error_msg or "couldn't find remote ref" in error_msg:
                    print("\033[93m提示：远程分支不存在\033[0m")
                    print("请检查远程仓库是否有 main 分支")
                else:
                    print("提示：请检查网络连接或仓库URL是否正确")
                break
        elif pull_choice in ['n', 'no']:
            print("跳过拉取")
            break
        else:
            print("\033[91m输入无效，请输入 y 或 n\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)
