"""最终清理"""
import subprocess
import os

def main():
    cwd = r"c:\Users\86159\yhh"
    fpath = os.path.join(cwd, "cleanup.py")
    if os.path.exists(fpath):
        os.remove(fpath)
    subprocess.run(["git", "add", "."], cwd=cwd, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: final cleanup"],
        cwd=cwd, capture_output=True, text=True
    )
    result = subprocess.run(
        ["git", "push"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    print(f"推送: {result.stdout}\n{result.stderr}\n返回码: {result.returncode}")
    # 自删除
    os.remove(os.path.join(cwd, "final_cleanup.py"))

if __name__ == "__main__":
    main()
