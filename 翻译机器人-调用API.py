import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

class SmartTranslator:
    def __init__(self):
        self.model=init_chat_model(
            model=os.getenv("LLM_MODEL_ID"),
            model_provider="openai",
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0.3,
        )
    def translate(self, text: str, target_language: str = "中文", style: str = "正式"):
        """
        翻译文本
        Args:
            text: 待翻译的文本
            target_language: 目标语言(中文/英文/日文等)
            style: 翻译风格（正式/口语/文学）
        """
        system_prompt = f"""
        你是一个翻译助手。
        任务：
        1.自动检测输入文本的语言
        2.翻译成{target_language}，翻译风格为{style}
        4.如果有专业术语，在翻译后用括号标注原文
        输出格式：
        原文：xxx
        翻译：xxx
        专业术语：(如果有专业术语，否则为空)
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text),
        ]
        response = self.model.invoke(messages)
        return response.content


def main():
    translator = SmartTranslator()
    print("智能翻译助手（Langchain 1.0）")
    print("="*50)
    text1 = "LangChain is a framework for developing applications powered by large language models."
    print(f"\n原文：{text1}")
    print(f"\n翻译结果：{translator.translate(text1,"中文","正式")}")
    print("="*50)
    test2= "这个框架真好用，强烈推荐！"
    print(f"\n原文：{test2}")
    print(f"\n翻译结果：{translator.translate(test2,"英文","口语")}")
    print("="*50)
    print("\n 进入交互模式（输入exit退出）\n")
    while True:
        user_input = input("请输入要翻译的文本：")
        if user_input.lower() == "exit":
            break
        target=input("请输入目标语言（默认中文）：")
        if not target:
            target="中文"
        style=input("请输入翻译风格（默认正式）：")
        if not style:
            style="正式"
        print(f"\n 翻译中...")
        result = translator.translate(user_input,target,style)
        print(f"\n翻译结果：{result}")
        print("="*50)
if __name__ == "__main__":
    main()
                    