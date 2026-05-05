import subprocess
import sys
import os
import hashlib

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

def generate_dynamic_hash():
    timestamp = str(os.times())
    return hashlib.md5(timestamp.encode()).hexdigest()[:8]

def delete_git_repo():
    try:
        git_dir = os.path.join(os.getcwd(), ".git")
        if not os.path.exists(git_dir):
            print("\033[91m删除失败: .git 目录不存在\033[0m")
            return False
        
        result = subprocess.run(
            f'rmdir /s /q "{git_dir}"',
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=True
        )
        if result.returncode == 0:
            print("本地git仓库已删除")
            return True
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"\033[91m删除失败: {error_msg}\033[0m")
            if "找不到指定的文件" in error_msg:
                print("提示：目录可能已被删除或路径不正确")
            else:
                print("提示：请尝试以管理员身份运行此程序")
            return False
    except Exception as e:
        print(f"\033[91m删除失败: {e}\033[0m")
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
    
    print("\n警告：此操作将删除本地git仓库（.git目录），但不会影响工作区文件")
    
    first_confirm = input("确认要删除本地git仓库吗？(yes/no): ").strip().lower()
    if first_confirm != 'yes':
        print("取消删除")
        sys.exit(0)
    
    dynamic_hash = generate_dynamic_hash()
    print(f"\n请输入以下哈希值进行确认: {dynamic_hash}")
    user_hash = input("输入哈希值: ").strip()
    if user_hash != dynamic_hash:
        print("哈希值不匹配，取消删除")
        sys.exit(0)
    
    third_confirm = input("\nHello, this program can only delete locally, are you sure? (yes/no): ").strip().lower()
    if third_confirm != 'yes':
        print("取消删除")
        sys.exit(0)
    
    delete_git_repo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)