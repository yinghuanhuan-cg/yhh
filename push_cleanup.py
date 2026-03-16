"""提交清理并推送"""
import subprocess

def main():
    cwd = r"c:\Users\86159\yhh"
    subprocess.run(["git", "add", "."], cwd=cwd, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: remove temp scripts"],
        cwd=cwd, capture_output=True, text=True
    )
    result = subprocess.run(
        ["git", "push"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    print(f"推送: {result.stdout}\n{result.stderr}\n返回码: {result.returncode}")
    import os
    os.remove(os.path.join(cwd, "push_cleanup.py"))

if __name__ == "__main__":
    main()
