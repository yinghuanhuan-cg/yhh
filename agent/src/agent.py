"""
核心 Agent 模块

封装 LLM 初始化、工具绑定、对话管理等核心逻辑。
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config import AppConfig, get_config
from src.prompts import get_system_prompt
from src.tools import get_all_tools


class YHHAgent:
    """YHH Agent 核心类"""

    def __init__(self, config: AppConfig | None = None):
        self.config = config or get_config()
        self.tools = get_all_tools()
        self.history: list = []

        # 初始化 LLM
        self.llm = ChatOpenAI(
            api_key=self.config.llm.api_key,
            base_url=self.config.llm.api_base,
            model=self.config.llm.model_name,
        )

        # 绑定工具
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

        # 系统提示词
        self.system_message = SystemMessage(
            content=get_system_prompt(self.config.agent.name)
        )

    def chat(self, user_input: str) -> str:
        """处理单轮对话

        Args:
            user_input: 用户输入

        Returns:
            Agent 的回复文本
        """
        # 构建消息列表
        messages = [self.system_message] + self.history + [HumanMessage(content=user_input)]

        # 调用 LLM
        response = self.llm_with_tools.invoke(messages)

        # 处理工具调用（简化版，实际可接入 LangGraph 做更复杂的流程）
        tool_results = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_map = {t.name: t for t in self.tools}
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                    tool_results.append({"tool": tool_name, "result": str(result)})

            # 如果有工具调用，将结果汇总后再次调用 LLM 生成最终回复
            if tool_results:
                tool_summary = "\n".join(
                    f"[{r['tool']}] 结果: {r['result']}" for r in tool_results
                )
                messages.append(response)
                messages.append(HumanMessage(content=f"工具调用结果:\n{tool_summary}"))
                response = self.llm.invoke(messages)

        reply = response.content if isinstance(response, AIMessage) else str(response)

        # 更新历史
        self.history.append(HumanMessage(content=user_input))
        self.history.append(AIMessage(content=reply))

        return reply

    def reset(self):
        """重置对话历史"""
        self.history.clear()

    def get_info(self) -> dict:
        """获取 Agent 信息"""
        return {
            "name": self.config.agent.name,
            "model": self.config.llm.model_name,
            "tools": [t.name for t in self.tools],
            "history_length": len(self.history),
        }


if __name__ == "__main__":
    agent = YHHAgent()
    info = agent.get_info()
    print(f"Agent: {info['name']}")
    print(f"模型: {info['model']}")
    print(f"工具: {', '.join(info['tools'])}")
