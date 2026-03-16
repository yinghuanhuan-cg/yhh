"""
Git 初始化并推送到 GitHub 的临时脚本
"""

import subprocess
import os


def run_cmd(cmd, cwd):
    """执行命令并打印输出"""
    print(f">>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


def main():
    repo_dir = r"c:\Users\86159\yhh"

    # 1. 初始化 git
    run_cmd(["git", "init"], cwd=repo_dir)

    # 2. 配置用户信息（如果未配置）
    run_cmd(["git", "config", "user.email", "yinghuanhuan-cg@users.noreply.github.com"], cwd=repo_dir)
    run_cmd(["git", "config", "user.name", "yinghuanhuan-cg"], cwd=repo_dir)

    # 3. 添加远程仓库
    run_cmd(["git", "remote", "add", "origin", "https://github.com/yinghuanhuan-cg/yhh.git"], cwd=repo_dir)

    # 4. 添加所有文件
    run_cmd(["git", "add", "."], cwd=repo_dir)

    # 5. 查看状态
    run_cmd(["git", "status"], cwd=repo_dir)

    # 6. 提交
    run_cmd(["git", "commit", "-m", "feat: 初始化 Agent 项目框架"], cwd=repo_dir)

    # 7. 设置主分支并推送
    run_cmd(["git", "branch", "-M", "main"], cwd=repo_dir)
    run_cmd(["git", "push", "-u", "origin", "main"], cwd=repo_dir)

    print("\n✅ 推送完成！")


if __name__ == "__main__":
    main()
