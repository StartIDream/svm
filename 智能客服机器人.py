import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

load_dotenv(".env")


class CustomerDatabase:
    def __init__(self):
        self.customer_data = {
            "user1": {
                "name": "张三",
                "phone": "13800000000",
                "email": "zhangsan@example.com",
                "address": "北京市海淀区",
                "level": "VIP",
            },
            "user2": {
                "name": "李四",
                "phone": "13900000000",
                "email": "lisi@example.com",
                "address": "北京市东城区",
                "level": "普通用户",
            },
        }
        self.order_data = {
            "user1": [
                {"order_id": "order1", "status": "未支付", "product": "商品A", "quantity": 2, "total_price": 100},
                {"order_id": "order2", "status": "已送达", "product": "商品B", "quantity": 1, "total_price": 50},
            ],
            "user2": [
                {"order_id": "order3", "status": "已发货", "product": "商品C", "quantity": 1, "total_price": 150},
            ],
        }

    def get_customer(self, user_id: str) -> Optional[dict]:
        """获取客户信息"""
        return self.customer_data.get(user_id)

    def get_order(self, user_id: str) -> list:
        """获取订单信息"""
        return self.order_data.get(user_id, [])


class ConversationStorage:
    def __init__(self, storage_file: str = "customer_service_history.json"):
        self.storage_file = storage_file

    def save(self, user_id: str, session_id: str, messages: list, metadata: dict = None):
        """保存会话记录"""
        data = self._load()
        if user_id not in data:
            data[user_id] = {}
        #序列化消息
        serialized = []
        for msg in messages:
            serialized.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat(),
            })
        data[user_id][session_id] = {
            "messages": serialized,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, user_id: str, session_id: str = None) -> list:
        """加载会话记录"""
        data = self._load()
        if user_id not in data or session_id not in data[user_id]:
            return []
        messages = []
        for msg in data[user_id][session_id]["messages"]:
            if msg["type"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["type"] == "ai":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["type"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
        return messages

    def list_sessions(self, user_id: str) -> list:
        """列出用户的所有会话"""
        data = self._load()
        if user_id not in data:
            return []
        return list(data[user_id].keys())

    def _load(self) -> dict:
        """加载会话记录文件"""
        if not os.path.exists(self.storage_file):
            return {}
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}


# 全局数据库实例
customer_db = CustomerDatabase()


@tool
def get_customer_info(user_id: str) -> str:
    """获取客户信息
    Args:
        user_id: 客户ID，如"user1"
    """
    customer = customer_db.get_customer(user_id)
    if customer:
        return f"""客户信息：
        姓名:{customer['name']},
        手机号:{customer['phone']},
        邮箱:{customer['email']},
        地址:{customer['address']},
        会员等级:{customer['level']}"""
    else:
        return f"未找到客户{user_id}的信息"


@tool
def get_order_info(user_id: str) -> str:
    """查询客户订单信息
    Args:
        user_id: 客户ID，如"user1"
    """
    orders = customer_db.get_order(user_id)
    if orders:
        result = ""
        for order in orders:
            result += f"订单号：{order['order_id']}\n"
            result += f"商品：{order['product']}\n"
            result += f"订单状态：{order['status']}\n"
            result += f"数量：{order['quantity']}\n"
            result += f"金额：{order['total_price']}\n"
            result += "=" * 40 + "\n"
        return result
    else:
        return f"未找到客户{user_id}的信息"


@tool
def get_order_status(order_id: str) -> str:
    """获取订单状态
    Args:
        order_id: 订单号 ，如"order1"
    """
    for user_id, orders in customer_db.order_data.items():
        for order in orders:
            if order['order_id'] == order_id:
                return f"""订单{order['order_id']}状态,
                            商品:{order['product']},
                            订单状态:{order['status']}"""
    return f"未找到订单{order_id}的信息"


@tool
def create_ticket(user_id: str, problem: str) -> str:
    """创建工单
    Args:
        user_id: 客户ID
        problem: 工单问题
    """
    ticket_id = f"ticket_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return f"""已为您创建工单：
    工单号：{ticket_id}
    工单问题：{problem}
    工单状态：处理中
    我们的工作人员会尽快联系您。感谢您的理解。
    """


@tool
def search_knowledge_base(keyword: str) -> str:
    """搜索知识库
    Args:
        keyword: 搜索关键词
    """
    #模拟知识库
    knowledge_base = {
        "退货": "退货政策：\n1.7天无理由退货\n2.商品需保持完好\n3.提供订单号和退货原因\n4.联系客服办理",
        "发票": "发票申请: \n1.登录账户\n2.进入订单详情\n3. 点击[申请发票]\n4.填写发票信息",
        "配送": "配送说明: \n1. 全国包邮(偏远地区除外)\n2.一般3-5个工作日送达\n3.可选择上门自提",
        "支付": "支付方式: \n1.微信支付\n2.支付宝\n3.银行卡\n4. 货到付款(部分地区)",
    }
    for key, value in knowledge_base.items():
        if keyword in key:
            return value
    return f"未找到与{keyword}相关的信息,请联系人工客服"


class CustomerServiceBot:
    def __init__(self):
        self.model = init_chat_model(
            model=os.getenv("LLM_MODEL_ID"),
            model_provider="openai",
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0.3,
        )
        self.tools = [
            get_customer_info,
            get_order_info,
            get_order_status,
            create_ticket,
            search_knowledge_base,
        ]
        system_prompt = """
        你的职责:
        1.礼貌、友好地回答客户问题
        2.使用工具查询订单、客户信息
        3.解答常见问题(退货、发票、配送等)
        4.无法解决时创建工单

        工作流程:
        1.首先确认客户身份(询问客户ID或订单号)
        2.了解客户问题
        3.使用合适的工具查询信息或解决问题
        4.用通俗易懂的语言回复客户
        5.如果无法解决，创建工单

        注意事项:
        1.始终保持礼貌、友好和专业
        2.回答问题要准确不要编造信息
        3.如果不确定，建议联系人工客服
        4.记住对话历史中的客户信息
        """
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        self.storage = ConversationStorage()
        self.current_user = None
        self.current_session = None
        self.messages = []

    def start_session(self, user_id: str, session_id: str = None):
        """开始与客户的对话"""
        self.current_user = user_id
        self.current_session = session_id or f"session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        #加载历史对话
        self.messages = self.storage.load(user_id, self.current_session)
        if not self.messages:
            welcome = f"欢迎客户，我是智能客服机器人,有什么我可以帮助您的吗？\n\n提示：告诉我您的用户ID"
            self.messages.append(AIMessage(content=welcome))

    def chat(self, message: str) -> str:
        """与客户进行对话"""
        #添加客户消息
        self.messages.append(HumanMessage(content=message))
        #调用智能体
        result = self.agent.invoke({"messages": self.messages})
        #更新对话历史
        self.messages = result["messages"]
        #保存对话历史
        self.storage.save(self.current_user, self.current_session, self.messages)
        #返回智能体回复
        for msg in reversed(self.messages):
            if msg.type == "ai" and msg.content:
                return msg.content
        return "抱歉我暂时无法处理您的请求"

    def end_session(self):
        """结束与客户的对话"""
        self.storage.save(
            self.current_user,
            self.current_session,
            self.messages,
            metadata={"ended_at": datetime.now().isoformat()},
        )


def main():
    bot = CustomerServiceBot()
    print("=" * 50)
    print(" 🤖 智能客服机器人（Langchain1.0版）")
    print("=" * 50)
    print("请输入您的客户ID（测试账号user1或user2）")
    user_id = input("客户ID：").strip() or "user1"
    #检查历史对话
    sessions = bot.storage.list_sessions(user_id)
    if sessions:
        print(f"您有{len(sessions)}个历史会话")
        print("会话列表：", ", ".join(sessions[-3:]))
        choice = input("\n继续上次对话？(y/n)").strip().lower()
        if choice == "y":
            bot.start_session(user_id, sessions[-1])
            print(f"✅ 继续上次对话：{sessions[-1]}")
        else:
            bot.start_session(user_id)
            print("✅ 开始新对话")
    else:
        bot.start_session(user_id)
        print(f"\n ✅ 欢迎新客户：{user_id}")

    if bot.messages:
        print(f"\n 🤖 {bot.messages[-1].content}\n")
    print("输入 'exit' 结束对话\n")
    while True:
        user_input = input("👤 您：")
        if user_input == "exit":
            bot.end_session()
            print("✅ 对话已保存")
            print(f"会话ID：{bot.current_session}")
            print("✅ 感谢您的使用,再见！")
            break
        if not user_input.strip():
            continue
        #与智能体对话
        response = bot.chat(user_input)
        print(f"\n 🤖： {response}\n")


if __name__ == "__main__":
    main()
