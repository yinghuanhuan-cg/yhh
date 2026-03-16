"""
ReAct Agent Loop 单元测试

使用 Mock LLM 测试循环逻辑，不依赖真实 API。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, ToolMessage

from src.agent import ChatResult, ToolCallRecord, YHHAgent
from src.config import AgentConfig, APIConfig, AppConfig, LLMConfig


def make_test_config(max_iterations: int = 10) -> AppConfig:
    """创建测试用配置"""
    return AppConfig(
        llm=LLMConfig(api_key="test-key", model_name="test-model"),
        agent=AgentConfig(name="TestAgent", max_iterations=max_iterations),
        api=APIConfig(port=9000),
    )


def make_ai_message(content: str, tool_calls: list | None = None) -> AIMessage:
    """构造 AI 响应消息"""
    msg = AIMessage(content=content)
    if tool_calls:
        msg.tool_calls = tool_calls
    return msg


class TestReActLoop:
    """ReAct 循环核心逻辑测试"""

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_no_tool_call(self, mock_get_tools, mock_llm_cls):
        """LLM 直接回答，不调工具 → 循环 1 次就退出"""
        mock_get_tools.return_value = []

        # Mock LLM 直接返回文本
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.return_value = make_ai_message("你好！我是测试助手。")
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        result = agent.chat_with_detail("你好")

        assert result.reply == "你好！我是测试助手。"
        assert result.tool_calls == []
        assert result.steps == 1
        assert len(agent.history) == 2  # HumanMessage + AIMessage

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_single_tool_call(self, mock_get_tools, mock_llm_cls):
        """调 1 次工具 → LLM 拿到结果后回答"""
        # 准备一个 mock 工具
        mock_tool = MagicMock()
        mock_tool.name = "get_current_time"
        mock_tool.invoke.return_value = "2026-03-16 14:50:00"
        mock_get_tools.return_value = [mock_tool]

        # Mock LLM：第 1 次调用返回工具请求，第 2 次返回最终回答
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            make_ai_message("", tool_calls=[{
                "id": "call_001",
                "name": "get_current_time",
                "args": {},
            }]),
            make_ai_message("现在是 2026-03-16 14:50:00。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        result = agent.chat_with_detail("现在几点了")

        assert result.reply == "现在是 2026-03-16 14:50:00。"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].tool_name == "get_current_time"
        assert result.tool_calls[0].result == "2026-03-16 14:50:00"
        assert result.tool_calls[0].error == ""

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_multi_step_tool_calls(self, mock_get_tools, mock_llm_cls):
        """调 2 次工具，验证多步循环正确工作"""
        # 准备两个 mock 工具
        mock_time_tool = MagicMock()
        mock_time_tool.name = "get_current_time"
        mock_time_tool.invoke.return_value = "2026-03-16 14:50:00"

        mock_calc_tool = MagicMock()
        mock_calc_tool.name = "calculate"
        mock_calc_tool.invoke.return_value = "190"

        mock_get_tools.return_value = [mock_time_tool, mock_calc_tool]

        # Mock LLM：3 次调用
        # 第 1 次：请求调用 get_current_time
        # 第 2 次：拿到时间后，请求调用 calculate
        # 第 3 次：拿到计算结果后，给出最终回答
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            make_ai_message("", tool_calls=[{
                "id": "call_001",
                "name": "get_current_time",
                "args": {},
            }]),
            make_ai_message("", tool_calls=[{
                "id": "call_002",
                "name": "calculate",
                "args": {"expression": "18*60 - (14*60+50)"},
            }]),
            make_ai_message("现在 14:50，距离 18:00 下班还有 190 分钟（约 3 小时 10 分钟）。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        result = agent.chat_with_detail("现在几点了，距离下班还有多久")

        assert "190" in result.reply or "3" in result.reply
        assert len(result.tool_calls) == 2
        assert result.tool_calls[0].tool_name == "get_current_time"
        assert result.tool_calls[1].tool_name == "calculate"
        assert result.steps == 3  # 循环了 3 步

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_max_iterations_guard(self, mock_get_tools, mock_llm_cls):
        """模拟 LLM 一直要调工具，验证到 max_iterations 后强制停止"""
        mock_tool = MagicMock()
        mock_tool.name = "calculate"
        mock_tool.invoke.return_value = "42"
        mock_get_tools.return_value = [mock_tool]

        # LLM 永远返回工具调用请求（模拟死循环）
        tool_call_response = make_ai_message("", tool_calls=[{
            "id": "call_loop",
            "name": "calculate",
            "args": {"expression": "1+1"},
        }])
        # max_iterations=3: 前 3 次都返回工具调用，第 4 次（强制结束后）返回最终回答
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            tool_call_response,
            tool_call_response,
            tool_call_response,
            make_ai_message("抱歉，达到了推理步数限制。基于已有信息，结果是 42。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config(max_iterations=3))
        result = agent.chat_with_detail("一直算")

        # 应该在 3 步后强制停止
        assert len(result.tool_calls) == 3
        assert "42" in result.reply

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_tool_execution_error(self, mock_get_tools, mock_llm_cls):
        """工具执行抛异常，验证不会整体崩溃"""
        mock_tool = MagicMock()
        mock_tool.name = "calculate"
        mock_tool.invoke.side_effect = ValueError("除以零错误")
        mock_get_tools.return_value = [mock_tool]

        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            make_ai_message("", tool_calls=[{
                "id": "call_err",
                "name": "calculate",
                "args": {"expression": "1/0"},
            }]),
            make_ai_message("抱歉，计算出错了。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        result = agent.chat_with_detail("计算 1/0")

        # 整体没有崩溃
        assert "抱歉" in result.reply or "出错" in result.reply
        # 工具调用记录中有错误信息
        assert len(result.tool_calls) == 1
        assert "除以零" in result.tool_calls[0].error
        assert result.tool_calls[0].result == ""

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_unknown_tool(self, mock_get_tools, mock_llm_cls):
        """LLM 请求调用一个不存在的工具"""
        mock_get_tools.return_value = []

        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            make_ai_message("", tool_calls=[{
                "id": "call_unknown",
                "name": "nonexistent_tool",
                "args": {},
            }]),
            make_ai_message("抱歉，该工具不可用。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        result = agent.chat_with_detail("用不存在的工具")

        assert len(result.tool_calls) == 1
        assert "未知工具" in result.tool_calls[0].error

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_chat_simple_interface(self, mock_get_tools, mock_llm_cls):
        """测试简单 chat() 接口保持兼容"""
        mock_get_tools.return_value = []
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.return_value = make_ai_message("兼容测试OK")
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        reply = agent.chat("测试")

        # chat() 返回纯字符串
        assert isinstance(reply, str)
        assert reply == "兼容测试OK"

    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.get_all_tools")
    def test_history_only_stores_final(self, mock_get_tools, mock_llm_cls):
        """验证对话历史只存 用户输入+最终回答，不存中间推理"""
        mock_tool = MagicMock()
        mock_tool.name = "get_current_time"
        mock_tool.invoke.return_value = "2026-03-16"
        mock_get_tools.return_value = [mock_tool]

        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = [
            make_ai_message("", tool_calls=[{"id": "c1", "name": "get_current_time", "args": {}}]),
            make_ai_message("今天是 2026-03-16。"),
        ]
        mock_llm_cls.return_value = mock_llm

        agent = YHHAgent(make_test_config())
        agent.chat("今天几号")

        # 历史应该只有 2 条：HumanMessage + AIMessage（不含中间 ToolMessage）
        assert len(agent.history) == 2
        assert agent.history[0].content == "今天几号"
        assert "2026-03-16" in agent.history[1].content
