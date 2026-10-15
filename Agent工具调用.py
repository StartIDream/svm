import os
import ast
import math
import operator
from dotenv import load_dotenv
from langchain_core import messages
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from datetime import datetime

load_dotenv(".env")


# 白名单：仅允许安全的数学函数与运算符
_ALLOWED_FUNCS = {
    "sqrt": math.sqrt, "pow": pow, "abs": abs,
    "log": math.log, "log10": math.log10, "log2": math.log2, "exp": math.exp,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
    "pi": math.pi, "e": math.e,
}
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(expr: str):
    """用 AST 白名单遍历器安全求值数学表达式，拒绝一切 eval 可利用的语法。"""
    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):                          # 字面量（Python 3.8+ 统一为 Constant）
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"不支持的常量: {node!r}")
        if isinstance(node, ast.Name):                              # 白名单常量（pi, e）
            if node.id in _ALLOWED_FUNCS and callable(_ALLOWED_FUNCS[node.id]) is False:
                return _ALLOWED_FUNCS[node.id]
            if node.id in _ALLOWED_FUNCS:                       # pi/e 等挂在 dict 里
                v = _ALLOWED_FUNCS[node.id]
                if not callable(v):
                    return v
            raise ValueError(f"不支持的标识符: {node.id}")
        if isinstance(node, ast.BinOp):                         # 二元运算
            op_type = type(node.op)
            if op_type not in _BIN_OPS:
                raise ValueError(f"不支持的二元运算符: {op_type.__name__}")
            return _BIN_OPS[op_type](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):                       # 一元运算（+/-）
            op_type = type(node.op)
            if op_type not in _UNARY_OPS:
                raise ValueError(f"不支持的一元运算符: {op_type.__name__}")
            return _UNARY_OPS[op_type](_eval(node.operand))
        if isinstance(node, ast.Call):                          # 白名单函数调用
            if not isinstance(node.func, ast.Name):
                raise ValueError("仅支持直接函数名调用，不支持属性访问")
            fname = node.func.id
            if fname not in _ALLOWED_FUNCS or not callable(_ALLOWED_FUNCS[fname]):
                raise ValueError(f"不支持的函数: {fname}")
            args = [_eval(a) for a in node.args]
            if node.keywords:
                raise ValueError("不支持关键字参数")
            return _ALLOWED_FUNCS[fname](*args)
        raise ValueError(f"不支持的语法节点: {type(node).__name__}")

    return _eval(tree)


@tool
def calculator(expression: str) -> str:
    """计算数学表达式
    支持基本运算 +、-、*、/、**、%，以及 sqrt、log、log10、log2、exp、
    sin、cos、tan、asin、acos、atan、atan2、abs、pow；常量 pi、e。
    Args:
        expression: 数学表达式字符串，如"2+3*4"、"sqrt(4)"、"sin(pi/2)"
    Returns:
        str: 计算结果
    Example:
        calculator("2+3*4") 返回 "14"
        calculator("sqrt(16)+abs(-3)") 返回 "7.0"
    """
    try:
        result = _safe_eval(expression.strip())
        return str(result)
    except SyntaxError as e:
        return f"语法错误：{e.msg}"
    except ValueError as e:
        return f"表达式不合法：{e}"
    except Exception as e:
        return f"计算错误：{str(e)}"


@tool
def current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间
    Args:
        timezone: 时区，默认"Asia/Shanghai"
    Returns:
        str: 当前时间字符串，格式为"YYYY-MM-DD HH:MM:SS"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def get_weather(city: str) -> str:
    """获取城市的天气
    Args:
        city: 城市名称，如"厦门"
    Returns:
        str: 天气描述，如"晴朗"或"雨天"
    """
    return f"{city}的天气是晴朗的"


def main():
    model = init_chat_model(
        model="Qwen/Qwen3-8B",
        model_provider="openai",
        api_key=os.getenv("API_KEY"),
        temperature=0.0,
        base_url="https://api.siliconflow.cn/v1",
    )
    agent = create_agent(
        model,
        tools=[calculator, current_time, get_weather],
        system_prompt="你是一个专业的计算助手，支持计算数学表达式、获取当前时间和查询天气。请用中文回答",
    )
    # print("简单Agent示例")
    # print("=" * 50)
    # print("测试1：时间查询")
    # print("=" * 50)
    # question1 = "现在几点？"
    # print(f"用户：{question1}\n")
    # result1 = agent.invoke({"messages": [{"role": "user", "content": question1}]})
    # print(f"助手：[{result1['messages'][-1].content}]\n")

    # # 测试2：计算
    # print("=" * 50)
    # print("测试2：计算")
    # print("=" * 50)
    # question2 = "2+3*4"
    # print(f"用户：{question2}\n")
    # result2 = agent.invoke({"messages": [{"role": "user", "content": question2}]})
    # print(f"助手：[{result2['messages'][-1].content}]\n")

    # # 测试3：混合任务
    # print("=" * 50)
    # print("测试3：混合任务")
    # print("=" * 50)
    # question3 = "现在几点？顺便算一下100/5"
    # print(f"用户：{question3}\n")
    # result3 = agent.invoke({"messages": [{"role": "user", "content": question3}]})
    # print(f"助手：[{result3['messages'][-1].content}]\n")

    print("=" * 50)
    print("测试多轮对话")
    print("=" * 50)
    messages = []
    while True:
        user_input = input("请输入指令或exit退出：")
        if user_input.lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})
        result = agent.invoke({"messages": messages})
        messages = result["messages"]
        last_message = messages[-1]
        if last_message.type == "ai":
            print(f"助手：{last_message.content}\n")
        print("=" * 50)


if __name__ == "__main__":
    main()
