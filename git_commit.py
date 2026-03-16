import subprocess
import sys

def run():
    repo_path = r'c:\Users\86159\yhh'
    try:
        print("1. 执行 git add .")
        subprocess.run(['git', 'add', '.'], check=True, cwd=repo_path)
        
        print("2. 执行 git commit")
        result = subprocess.run(
            ['git', 'commit', '-m', 'feat(agent): 实现 ReAct Agent Loop，支持多步推理和工具调用'], 
            cwd=repo_path, 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
        
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"Commit 失败: {result.stderr}")
            return
            
        print("3. 执行 git push")
        push_result = subprocess.run(['git', 'push'], cwd=repo_path, capture_output=True, text=True)
        print(push_result.stdout)
        if push_result.returncode != 0:
            print(f"Push 失败: {push_result.stderr}")
        else:
            print("✅ 代码已成功提交并推送到远程仓库！")
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    run()
