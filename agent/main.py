"""
YHH Agent 入口文件

支持两种运行模式:
  - cli: 命令行交互模式
  - api: FastAPI HTTP 服务模式
"""

import sys

from src.agent import YHHAgent
from src.config import get_config


def run_cli():
    """命令行交互模式"""
    config = get_config()
    agent = YHHAgent(config)

    print(f"\n🤖 {config.agent.name} 已启动！(ReAct 模式)")
    print(f"   模型: {config.llm.model_name}")
    print(f"   工具: {', '.join(t.name for t in agent.tools)}")
    print(f"   最大推理步数: {config.agent.max_iterations}")
    print("   输入 'quit' 退出，输入 'reset' 重置对话\n")

    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("👋 再见！")
                break
            if user_input.lower() == "reset":
                agent.reset()
                print("🔄 对话历史已清除\n")
                continue

            # 使用详细接口，展示工具调用过程
            result = agent.chat_with_detail(user_input)

            # 打印工具调用链
            if result.tool_calls:
                print()
                for record in result.tool_calls:
                    args_str = ", ".join(f'{k}="{v}"' for k, v in record.tool_args.items())
                    if record.error:
                        print(f"  ❌ 步骤{record.step} {record.tool_name}({args_str}) → 失败: {record.error}")
                    else:
                        # 截断过长的结果显示
                        display_result = record.result[:80] + "..." if len(record.result) > 80 else record.result
                        print(f"  🔧 步骤{record.step} {record.tool_name}({args_str}) → {display_result}")

            print(f"\n🤖 {config.agent.name}: {result.reply}\n")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break


def run_api():
    """API 服务模式"""
    import uvicorn

    from src.api import app
    from src.config import get_config

    config = get_config()
    print(f"\n🚀 启动 {config.agent.name} API 服务...")
    uvicorn.run(app, host=config.api.host, port=config.api.port)


if __name__ == "__main__":
    mode = "cli"
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == "api":
                mode = "api"
                break

    if mode == "api":
        run_api()
    else:
        run_cli()
