"""
配置管理模块

从 .env 文件和环境变量加载所有配置项。
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class LLMConfig:
    """LLM 相关配置"""

    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    api_base: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    )
    model_name: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL_NAME", "gpt-4o"))


@dataclass
class AgentConfig:
    """Agent 相关配置"""

    name: str = field(default_factory=lambda: os.getenv("AGENT_NAME", "YHH-Agent"))
    max_iterations: int = field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    )
    verbose: bool = field(
        default_factory=lambda: os.getenv("AGENT_VERBOSE", "true").lower() == "true"
    )


@dataclass
class APIConfig:
    """API 服务配置"""

    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))


@dataclass
class AppConfig:
    """应用总配置"""

    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    api: APIConfig = field(default_factory=APIConfig)


def get_config() -> AppConfig:
    """获取应用配置单例"""
    return AppConfig()


if __name__ == "__main__":
    config = get_config()
    print(f"Agent 名称: {config.agent.name}")
    print(f"LLM 模型: {config.llm.model_name}")
    print(f"API 端口: {config.api.port}")
