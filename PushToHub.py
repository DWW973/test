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

def get_commit_message():
    while True:
        message = input("请输入提交信息: ").strip()
        if message:
            return message
        print("\033[91m提交信息不能为空，请重新输入\033[0m")

def check_git_config():
    try:
        result = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if not result.stdout.strip():
            return False, "user.name 未配置"
        
        result = subprocess.run(
            ["git", "config", "--get", "user.email"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if not result.stdout.strip():
            return False, "user.email 未配置"
        
        return True, ""
    except Exception as e:
        return False, str(e)

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

def main():
    if not check_git_installed():
        print("\033[91m未安装git工具\033[0m")
        sys.exit(1)
    
    print("git工具已安装")
    
    if not has_git_repo():
        print("\033[91m当前目录不是git仓库\033[0m")
        print("请先运行 InitHub.py 初始化仓库")
        sys.exit(1)
    
    print("当前目录是git仓库")
    
    config_ok, config_msg = check_git_config()
    if not config_ok:
        print(f"\033[91mgit配置错误: {config_msg}\033[0m")
        print("请运行以下命令配置git:")
        print("  git config --global user.name \"Your Name\"")
        print("  git config --global user.email \"your.email@example.com\"")
        sys.exit(1)
    
    try:
        print("检查是否有未提交的更改...")
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if not result.stdout.strip():
            print("\033[93m没有需要提交的更改\033[0m")
            sys.exit(0)
    except Exception as e:
        print(f"\033[93m检查状态失败: {e}\033[0m")
    
    try:
        print("添加所有文件...")
        result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("文件已添加")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m添加文件失败: {e.stderr.strip() or e.stdout.strip()}\033[0m")
        sys.exit(1)
    
    commit_message = get_commit_message()
    
    try:
        print("提交更改...")
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("提交成功")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "未知错误"
        print(f"\033[91m提交失败: {error_msg}\033[0m")
        sys.exit(1)
    
    try:
        print("推送到远程仓库...")
        branch = get_current_branch()
        print(f"当前分支: {branch}")
        
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        print("推送成功")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip()
        print(f"\033[91m推送失败: {error_msg}\033[0m")
        if "src refspec" in error_msg or "does not match any" in error_msg:
            print("\033[93m提示：可能是因为本地没有提交记录，或分支名称不匹配\033[0m")
            print("请确保已经执行过 git commit，或尝试以下命令:")
            print(f"  git push -u origin {branch}")
        else:
            print("提示：请检查网络连接或确保已设置正确的远程仓库")
        sys.exit(1)

if __name__ == "__main__":
    main()
