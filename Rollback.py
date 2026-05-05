import subprocess
import sys
import os

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

def get_commit_history():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "10"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip()
        if "does not have any commits yet" in error_msg:
            return "当前分支没有提交记录"
        return f"获取提交历史失败: {error_msg}"

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

def rollback_to_commit(commit_hash):
    try:
        print(f"正在回滚到提交: {commit_hash}")
        result = subprocess.run(
            ["git", "reset", "--hard", commit_hash],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("本地回滚成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m回滚失败: {e.stderr.strip()}\033[0m")
        return False

def force_push(branch):
    try:
        print(f"正在强制推送到远程仓库...")
        result = subprocess.run(
            ["git", "push", "-f", "origin", branch],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("强制推送成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m强制推送失败: {e.stderr.strip()}\033[0m")
        return False

def main():
    if not check_git_installed():
        print("\033[91m未安装git工具\033[0m")
        sys.exit(1)
    
    print("git工具已安装")
    
    if not has_git_repo():
        print("\033[91m当前目录不是git仓库\033[0m")
        sys.exit(1)
    
    print("当前目录是git仓库")
    
    print("\n最近的提交历史:")
    print("-" * 60)
    history = get_commit_history()
    print(history)
    print("-" * 60)
    
    if "没有提交记录" in history:
        print("\033[93m提示：当前分支没有提交记录，无法回滚\033[0m")
        sys.exit(0)
    
    commit_hash = input("\n请输入要回滚到的提交哈希值: ").strip()
    if not commit_hash:
        print("\033[91m提交哈希值不能为空\033[0m")
        sys.exit(1)
    
    branch = get_current_branch()
    confirm = input(f"确认要回滚到 {commit_hash} 吗？这将丢弃之后的所有提交 (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("取消回滚")
        sys.exit(0)
    
    if rollback_to_commit(commit_hash):
        push_confirm = input(f"\n是否将回滚强制推送到远程仓库 origin/{branch}？这将覆盖远程仓库的提交 (y/n): ").strip().lower()
        if push_confirm in ['y', 'yes']:
            force_push(branch)
        else:
            print("已跳过强制推送，远程仓库未更新")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)