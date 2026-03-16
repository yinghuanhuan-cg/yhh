"""
FastAPI 接口层

提供 HTTP API 接口供外部调用 Agent 服务。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import __version__
from src.agent import YHHAgent
from src.config import get_config
from src.models import ChatRequest, ChatResponse, HealthResponse

# 初始化
config = get_config()
app = FastAPI(
    title=f"{config.agent.name} API",
    version=__version__,
    description="YHH Agent API 服务",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent 实例
agent = YHHAgent(config)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="ok",
        agent_name=config.agent.name,
        version=__version__,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口

    发送消息给 Agent，获取回复。
    支持 ReAct 多步推理，返回工具调用记录。
    """
    result = agent.chat_with_detail(request.message)
    return ChatResponse(
        reply=result.reply,
        tool_calls=[
            {"tool": r.tool_name, "args": r.tool_args, "result": r.result, "step": r.step}
            for r in result.tool_calls
        ],
    )


@app.post("/reset")
async def reset_conversation():
    """重置对话历史"""
    agent.reset()
    return {"status": "ok", "message": "对话历史已清除"}


@app.get("/info")
async def agent_info():
    """获取 Agent 信息"""
    return agent.get_info()
