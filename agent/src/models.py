"""
数据模型定义

使用 Pydantic 定义请求/响应等数据模型。
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """聊天消息"""

    role: str = Field(description="消息角色: user / assistant / system")
    content: str = Field(description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str = Field(description="用户输入的消息")
    history: list[ChatMessage] = Field(default_factory=list, description="历史对话记录")


class ChatResponse(BaseModel):
    """聊天响应"""

    reply: str = Field(description="Agent 回复内容")
    tool_calls: list[dict] = Field(default_factory=list, description="工具调用记录")


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = "ok"
    agent_name: str = ""
    version: str = ""
