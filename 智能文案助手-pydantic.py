import os
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from typing import List, Literal
import json
from datetime import datetime

load_dotenv()


class CopywritingScore(BaseModel):
    creativity: int = Field(description="创意性，1-10分")
    clarity: int = Field(description="清晰度，1-10分")
    appeal: int = Field(description="吸引力，1-10分")
    overall: int = Field(description="总分，1-100分")
    comment: str = Field(description="简短的评语")


class Copywriting(BaseModel):
    """文案结果"""

    content: str = Field(description="文案内容")
    score: CopywritingScore = Field(description="质量评分")


class CopywritingBatch(BaseModel):
    """文案批量结果"""

    results: List[Copywriting] = Field(description="文案列表")


class SmmrCopywriting:
    """智能文案生成器"""

    def __init__(self):
        self.model = init_chat_model(
            model=os.getenv("LLM_MODEL_ID"),
            model_provider="openai",
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0.9,
        )
        self.structured_model = self.model.with_structured_output(CopywritingBatch)

    def generate(
        self,
        product: str,
        copy_type: Literal["广告", "社交媒体", "邮件", "博客"],
        style: Literal["正式", "轻松", "专业", "幽默"],
        count: int = 3,
    ) -> List[Copywriting]:
        """生成文案
        Args:
            product: 产品名称或服务描述
            copy_type: 文案类型（广告/社交媒体/邮件/博客）
            style: 文案风格（正式/轻松/专业/幽默）
            count: 生成文案数量
        Returns:
            List[Copywriting]: 生成的文案列表
        """
        prompt = f"""
            你是一个专业的文案撰写专家。
            任务：为以下产品创作{copy_type}文案，文案风格为{style}。
            产品信息：{product}
            要求：
            文案类型：{copy_type}
            文案风格：{style}
            生成数量：{count}不同版本的文案
            每个文案都要有创意，不能重复
            每个文案打分并给出评语

            输出：
            请输出{count}个文案，每个文案包含内容和评分。
            """
        result = self.structured_model.invoke(prompt)
        return result.results

    def export_to_json(self, copies: List[Copywriting], filename: str = None):
        """导出文案到JSON文件"""
        if filename is None:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            "generated_at": datetime.now().isoformat(),
            "copies": [
                {
                    "content": c.content,
                    "score": {
                        "creativity": c.score.creativity,
                        "clarity": c.score.clarity,
                        "appeal": c.score.appeal,
                        "overall": c.score.overall,
                        "comment": c.score.comment,
                    },
                }
                for c in copies
            ],
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


def main():
    copywriter = SmmrCopywriting()
    print("=" * 50)
    print("智能文案生成器（Langchain 1.0）")
    print("=" * 50)
    productl = """
    产品：AI编程助手
    特点：
    实时代码补全
    智能错误检测
    支持20+编程语言
    提高开发效率50%
    """
    copies = copywriter.generate(productl, "广告", "专业", 3)
    for i, copy in enumerate[Copywriting](copies, 1):
        print(f"\n版本 {i}:")
        print(f"文案内容：{copy.content}")
        print(
            f"评分： 创意{copy.score.creativity} | 清晰度{copy.score.clarity} | "
            f"吸引力{copy.score.appeal} | 总分{copy.score.overall} "
            f"评语{copy.score.comment}"
        )
    #导出
    print("=" * 50)
    filename = copywriter.export_to_json(copies)
    print(f"已导出到 {filename}")


if __name__ == "__main__":
    main()
