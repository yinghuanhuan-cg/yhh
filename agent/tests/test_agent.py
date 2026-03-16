"""
Agent 核心逻辑单元测试
"""

import sys
import os

# 将 agent 目录加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import AppConfig, LLMConfig, AgentConfig, APIConfig
from src.models import ChatRequest, ChatResponse, HealthResponse
from src.prompts import get_system_prompt
from src.tools import get_all_tools, get_current_time, calculate


class TestConfig:
    """配置模块测试"""

    def test_default_config(self):
        config = AppConfig()
        assert config.agent.name is not None
        assert config.llm.model_name is not None
        assert config.api.port > 0

    def test_custom_config(self):
        config = AppConfig(
            llm=LLMConfig(api_key="test-key", model_name="gpt-3.5-turbo"),
            agent=AgentConfig(name="TestAgent", max_iterations=5),
            api=APIConfig(port=9000),
        )
        assert config.llm.api_key == "test-key"
        assert config.agent.name == "TestAgent"
        assert config.api.port == 9000


class TestModels:
    """数据模型测试"""

    def test_chat_request(self):
        req = ChatRequest(message="你好")
        assert req.message == "你好"
        assert req.history == []

    def test_chat_response(self):
        resp = ChatResponse(reply="你好！")
        assert resp.reply == "你好！"
        assert resp.tool_calls == []

    def test_health_response(self):
        health = HealthResponse(agent_name="Test", version="0.1.0")
        assert health.status == "ok"


class TestPrompts:
    """Prompt 模板测试"""

    def test_system_prompt_default(self):
        prompt = get_system_prompt()
        assert "YHH-Agent" in prompt

    def test_system_prompt_custom_name(self):
        prompt = get_system_prompt("CustomBot")
        assert "CustomBot" in prompt


class TestTools:
    """工具模块测试"""

    def test_get_all_tools(self):
        tools = get_all_tools()
        assert len(tools) >= 3
        names = [t.name for t in tools]
        assert "get_current_time" in names
        assert "calculate" in names
        assert "search_knowledge" in names

    def test_calculate_tool(self):
        result = calculate.invoke({"expression": "2 + 3 * 4"})
        assert result == "14"

    def test_calculate_invalid(self):
        result = calculate.invoke({"expression": "import os"})
        assert "错误" in result or "不允许" in result

    def test_get_current_time(self):
        result = get_current_time.invoke({})
        assert len(result) > 0
        # 应该包含日期格式
        assert "-" in result
