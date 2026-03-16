"""清理临时 git 脚本并追加提交"""
import subprocess
import os

def main():
    cwd = r"c:\Users\86159\yhh"

    # 删除临时脚本
    for f in ["git_init_push.py", "git_push.py", "git_check.py"]:
        fpath = os.path.join(cwd, f)
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"已删除: {f}")

    # 追加提交清理
    subprocess.run(["git", "add", "."], cwd=cwd, capture_output=True, text=True)
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    status = result.stdout.strip()
    if status:
        print(f"待提交变更:\n{status}")
        subprocess.run(
            ["git", "commit", "-m", "chore: remove temp scripts"],
            cwd=cwd, capture_output=True, text=True
        )
        result = subprocess.run(
            ["git", "push"],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        print(f"推送结果: {result.stdout}\n{result.stderr}")
    else:
        print("无待提交变更")

if __name__ == "__main__":
    main()
