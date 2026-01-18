"""
AI API异步客户端
使用asyncio提供更高的并发性能
"""
import asyncio
from openai import AsyncOpenAI
from config import config
from utils.retry_decorator import retry_with_backoff


class AsyncAIClient:
    """异步AI客户端类"""

    def __init__(self):
        """初始化异步AI客户端"""
        config.validate()
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = config.OPENAI_MODEL

    async def translate_text_async(self, text: str, source_lang: str = "auto", target_lang: str = "Chinese") -> str:
        """
        异步翻译文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的文本
        """
        if not text or not text.strip():
            return ""

        prompt = f"""请将以下文本翻译成{target_lang}。
只返回翻译结果，不要添加任何解释或额外内容。

原文：
{text}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一个专业的翻译助手，擅长将各种语言翻译成{target_lang}。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"翻译失败: {str(e)}")

    async def translate_batch_async(self, texts: list, source_lang: str = "auto", target_lang: str = "Chinese") -> list:
        """
        异步批量翻译文本

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []

        # 使用更可靠的编号格式
        numbered_texts = []
        for i, text in enumerate(texts, 1):
            numbered_texts.append(f"[{i}] {text}")

        combined_text = "\n".join(numbered_texts)

        prompt = f"""请将以下编号的文本翻译成{target_lang}。

严格要求：
1. 必须保持编号格式 [1], [2], [3] 等
2. 每个编号后只输出翻译结果，不要换行，不要分段
3. 必须与原文的编号数量完全一致（{len(texts)}个）
4. 不要添加任何解释、注释或额外内容
5. 如果原文是一行，翻译也必须是一行

原文：
{combined_text}

务必返回{len(texts)}行翻译结果，每行格式：[数字] 翻译内容"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一个专业的翻译助手。你必须严格按照用户要求的格式返回翻译结果，保持编号格式和顺序。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            # 解析翻译结果
            translated_text = response.choices[0].message.content.strip()
            lines = translated_text.split('\n')

            # 使用字典存储，按编号索引
            translated_dict = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 尝试解析编号格式 [数字]
                if line.startswith('[') and ']' in line:
                    try:
                        bracket_end = line.index(']')
                        number_str = line[1:bracket_end].strip()
                        number = int(number_str)
                        content = line[bracket_end + 1:].strip()

                        # 只保留有效编号范围内的结果
                        if 1 <= number <= len(texts):
                            translated_dict[number] = content
                    except (ValueError, IndexError):
                        continue

            # 按顺序构建结果列表
            translated_list = []
            for i in range(1, len(texts) + 1):
                if i in translated_dict:
                    translated_list.append(translated_dict[i])
                else:
                    translated_list.append(None)

            # 检查是否有缺失
            if None in translated_list or len(translated_list) != len(texts):
                print(f"警告: 异步批量翻译结果不完整，fallback到逐个翻译")
                # 使用普通客户端的逐个翻译
                from ai_client import ai_client
                return [ai_client.translate_text(text, source_lang, target_lang) for text in texts]

            return translated_list
        except Exception as e:
            print(f"异步批量翻译失败: {str(e)}")
            # 失败时fallback
            from ai_client import ai_client
            return [ai_client.translate_text(text, source_lang, target_lang) for text in texts]


# 创建全局异步客户端实例
async_ai_client = AsyncAIClient()
