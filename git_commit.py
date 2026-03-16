import subprocess

def run():
    repo_path = r'c:\Users\86159\yhh'
    try:
        print("1. 执行 git add .")
        subprocess.run(['git', 'add', '.'], check=True, cwd=repo_path)
        
        print("2. 执行 git commit")
        result = subprocess.run(
            ['git', 'commit', '-m', 'docs(agent): 更新 README，添加 ReAct 功能特性说明'], 
            cwd=repo_path, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"Commit 失败: {result.stderr}")
            return
            
        print("3. 执行 git push")
        push_result = subprocess.run(['git', 'push'], cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(push_result.stdout)
        if push_result.returncode != 0:
            print(f"Push 失败: {push_result.stderr}")
        else:
            print("✅ README 文档已成功更新并推送到远程仓库！")
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    run()
