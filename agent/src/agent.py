"""
核心 Agent 模块

封装 LLM 初始化、工具绑定、ReAct 循环等核心逻辑。
ReAct 模式: 思考(Reasoning) → 行动(Acting) → 观察(Observation) → 循环
"""

from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from src.config import AppConfig, get_config
from src.prompts import get_system_prompt
from src.tools import get_all_tools


@dataclass
class ToolCallRecord:
    """单次工具调用记录"""

    step: int
    tool_name: str
    tool_args: dict
    result: str
    error: str = ""


@dataclass
class ChatResult:
    """对话结果（包含推理过程）"""

    reply: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    steps: int = 0


class YHHAgent:
    """YHH Agent 核心类

    支持 ReAct 模式：LLM 可以多步调用工具进行推理，
    直到得出最终答案或达到最大迭代次数。
    """

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

        # 工具名 → 工具对象 映射
        self._tool_map = {t.name: t for t in self.tools}

        # 系统提示词
        self.system_message = SystemMessage(
            content=get_system_prompt(self.config.agent.name)
        )

    def chat(self, user_input: str) -> str:
        """处理对话（简单接口，兼容旧代码）

        Args:
            user_input: 用户输入

        Returns:
            Agent 的回复文本
        """
        result = self.chat_with_detail(user_input)
        return result.reply

    def chat_with_detail(self, user_input: str) -> ChatResult:
        """处理对话（详细接口，返回完整推理过程）

        ReAct 循环：
        1. 把用户输入发给 LLM
        2. 如果 LLM 返回工具调用请求 → 执行工具 → 把结果反馈给 LLM → 回到 2
        3. 如果 LLM 不再请求工具 → 提取最终回答 → 结束

        Args:
            user_input: 用户输入

        Returns:
            ChatResult 包含回复文本和工具调用记录
        """
        tool_call_log: list[ToolCallRecord] = []

        try:
            # 构建消息列表
            messages = [self.system_message] + self.history + [HumanMessage(content=user_input)]

            max_steps = self.config.agent.max_iterations
            step = 0

            for step in range(1, max_steps + 1):
                # 调用 LLM（带工具绑定）
                response = self.llm_with_tools.invoke(messages)

                # 没有工具调用 → LLM 已得出最终回答，退出循环
                if not self._has_tool_calls(response):
                    break

                # ---- 有工具调用 → 执行工具 ----
                messages.append(response)  # 追加 AI 的工具调用请求

                for tool_call in response.tool_calls:
                    record = self._execute_tool(step, tool_call)
                    tool_call_log.append(record)

                    # 使用标准 ToolMessage 格式反馈结果
                    messages.append(
                        ToolMessage(
                            content=record.result if not record.error else f"工具执行失败: {record.error}",
                            tool_call_id=tool_call["id"],
                        )
                    )
            else:
                # for-else: 循环正常耗尽（达到 max_iterations），强制生成最终回答
                if self._has_tool_calls(response):
                    messages.append(response)
                    messages.append(
                        HumanMessage(
                            content="[系统提示] 已达到最大推理步数限制，请根据目前已有的信息给出最终回答。"
                        )
                    )
                    response = self.llm.invoke(messages)

            # 提取最终回复
            reply = response.content if isinstance(response, AIMessage) else str(response)

            # 更新对话历史（只存用户输入和最终回答，不存中间推理过程）
            self.history.append(HumanMessage(content=user_input))
            self.history.append(AIMessage(content=reply))

            return ChatResult(reply=reply, tool_calls=tool_call_log, steps=step)

        except Exception as e:
            return ChatResult(reply=f"⚠️ 调用出错: {e}", tool_calls=tool_call_log, steps=0)

    def _has_tool_calls(self, response: AIMessage) -> bool:
        """检查 LLM 响应是否包含工具调用"""
        return hasattr(response, "tool_calls") and bool(response.tool_calls)

    def _execute_tool(self, step: int, tool_call: dict) -> ToolCallRecord:
        """安全执行单个工具调用

        Args:
            step: 当前推理步骤序号
            tool_call: LLM 返回的工具调用信息

        Returns:
            ToolCallRecord 工具调用记录
        """
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})

        if tool_name not in self._tool_map:
            return ToolCallRecord(
                step=step, tool_name=tool_name, tool_args=tool_args,
                result="", error=f"未知工具: {tool_name}",
            )

        try:
            result = self._tool_map[tool_name].invoke(tool_args)
            return ToolCallRecord(
                step=step, tool_name=tool_name, tool_args=tool_args,
                result=str(result),
            )
        except Exception as e:
            return ToolCallRecord(
                step=step, tool_name=tool_name, tool_args=tool_args,
                result="", error=str(e),
            )

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
            "max_iterations": self.config.agent.max_iterations,
        }


if __name__ == "__main__":
    agent = YHHAgent()
    info = agent.get_info()
    print(f"Agent: {info['name']}")
    print(f"模型: {info['model']}")
    print(f"工具: {', '.join(info['tools'])}")
    print(f"最大推理步数: {info['max_iterations']}")
