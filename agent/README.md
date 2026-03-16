# 🤖 YHH Agent

基于 **LangChain** 的智能 AI Agent 框架，支持自定义工具、多轮对话和 API 服务。

## ✨ 功能特性

- 🧠 **智能对话** - 基于 LLM 的多轮对话能力
- 🔄 **ReAct 引擎** - 支持多步推理与自主工具调用循环 (AI 思考链)
- 🔧 **工具扩展** - 灵活的自定义工具注册机制
- 📝 **Prompt 管理** - 模板化的 Prompt 管理
- 🌐 **API 服务** - FastAPI 驱动的 HTTP 接口，带工具调用轨迹返回
- ⚙️ **配置灵活** - 支持多种 LLM 后端切换

## 📁 项目结构

```
agent/
├── main.py              # 入口文件
├── src/
│   ├── agent.py         # 核心 Agent 逻辑
│   ├── tools.py         # 自定义工具
│   ├── prompts.py       # Prompt 模板
│   ├── config.py        # 配置管理
│   ├── models.py        # 数据模型
│   └── api.py           # FastAPI 接口
└── tests/
    └── test_agent.py    # 单元测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd agent
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

### 3. 运行

```bash
# 命令行交互模式
python main.py

# 启动 API 服务
python main.py --mode api
```

## 🧪 测试

```bash
pytest tests/ -v
```

## 📄 License

MIT
