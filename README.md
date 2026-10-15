# SVM 智能体实践项目

本项目是基于 Python 的多智能体（Multi-Agent）开发实践仓库，涵盖 AutoGen、LangGraph、LangChain 等主流框架，以及 Pydantic 数据校验、信息抽取、文案生成等应用场景。

## 项目结构

| 文件 | 框架/库 | 功能描述 |
|------|---------|---------|
| [AutoGen框架开发实践.py](AutoGen框架开发实践.py) | AutoGen | 多智能体软件开发团队（产品经理 + 工程师 + 代码审查员 + 用户代理）协作完成比特币价格显示应用 |
| [三步问答助手.py](三步问答助手.py) | LangGraph + LangChain | 三步流程搜索问答：理解查询 → Tavily 搜索 → 综合生成答案 |
| [Agent工具调用.py](Agent工具调用.py) | LangChain (Tools) | 安全的数学表达式求值（AST 白名单遍历，无 eval）、获取时间/天气 |
| [智能文案助手-pydantic.py](智能文案助手-pydantic.py) | Pydantic | 基于 Pydantic 模型的文案生成与评分系统，支持 JSON 导出 |
| [智能客服机器人.py](智能客服机器人.py) | LangChain | 客服场景对话机器人 |
| [翻译机器人-调用API.py](翻译机器人-调用API.py) | API 调用 | 调用外部 API 实现翻译功能 |
| [提词器.py](提词器.py) | 基础 Python | 信息抽取（NER）任务，JSON 格式输出实体 |
| [连通性测试.py](连通性测试.py) | 基础 Python | API 连通性测试脚本 |

## 环境配置

### 1. 创建 .env 文件

项目根目录下创建 `.env` 文件（**已加入 .gitignore，不会提交到 Git**）：

```env
# LLM 配置（SiliconFlow / OpenAI 兼容）
LLM_MODEL_ID=Qwen/Qwen3-8B
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://api.siliconflow.cn/v1

# Tavily 搜索（可选，未配置则回退到 LLM 知识）
TAVILY_API_KEY=你的Tavily密钥

# SerpAPI（可选）
SERPAPI_API_KEY=你的SerpAPI密钥
```

### 2. 安装依赖

```bash
pip install autogen-agentchat autogen-ext python-dotenv
pip install langgraph langchain-openai tavily-python
pip install pydantic rich transformers
```

## 快速开始

### AutoGen 多智能体团队

```bash
python AutoGen框架开发实践.py
```

四个智能体协作：产品经理分析需求 → 工程师写代码 → 代码审查员审查 → 用户代理验收。

### LangGraph 搜索问答

```bash
python 三步问答助手.py
```

交互式输入问题，系统经过「理解 → 搜索 → 回答」三步流程返回结果。

### 安全数学计算

```bash
python Agent工具调用.py
```

演示 `_safe_eval` AST 白名单求值器，支持 `+ - * / ** sqrt sin cos` 等运算，**完全替代 eval，无注入风险**。

## 技术亮点

- **AutoGen 0.4+ 新 API**：`autogen-agentchat` + `autogen-ext` 拆分包结构
- **LangGraph 状态机**：三步节点线性编排（understand → search → answer）
- **AST 安全求值**：自定义 `_safe_eval` 遍历器，拒绝 `__import__`/`lambda`/`getattr` 等恶意语法
- **Pydantic 数据校验**：文案评分模型强制类型约束
- **.env 环境隔离**：所有 API Key 集中管理，`.gitignore` 排除防止泄露

## 注意事项

- `.env` 文件包含敏感信息，**切勿提交到 Git**
- `__pycache__/` 和 IDE 配置已加入 `.gitignore`
- Python 3.12+ 环境，部分库需使用 `python -m pip` 安装

## License

MIT
