"""
自定义工具模块

定义 Agent 可以调用的各类工具。
使用 LangChain 的 @tool 装饰器注册工具。
"""

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。输入一个数学表达式字符串，返回计算结果。

    Args:
        expression: 数学表达式，例如 "2 + 3 * 4"
    """
    try:
        # 安全地计算数学表达式
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库中的信息。

    Args:
        query: 搜索关键词
    """
    # TODO: 接入实际的知识库（向量数据库、ES 等）
    return f"[知识库搜索] 暂未配置知识库，查询内容: {query}"


def get_all_tools() -> list:
    """获取所有注册的工具列表"""
    return [
        get_current_time,
        calculate,
        search_knowledge,
    ]


if __name__ == "__main__":
    tools = get_all_tools()
    print(f"已注册 {len(tools)} 个工具:")
    for t in tools:
        print(f"  - {t.name}: {t.description}")
