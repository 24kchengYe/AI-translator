"""
AI API客户端
用于与OpenRouter API交互
"""
from openai import OpenAI
from config import config
from utils.retry_decorator import retry_with_backoff


class AIClient:
    """AI客户端类"""

    def __init__(self):
        """初始化AI客户端"""
        config.validate()
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = config.OPENAI_MODEL

    @retry_with_backoff()
    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "Chinese") -> str:
        """
        翻译文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言，默认auto自动检测
            target_lang: 目标语言，默认Chinese

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
            response = self.client.chat.completions.create(
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

    @retry_with_backoff()
    def translate_batch(self, texts: list, source_lang: str = "auto", target_lang: str = "Chinese") -> list:
        """
        批量翻译文本（优化API调用）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []

        # 使用特殊分隔符合并文本
        separator = "\n###TRANSLATE_SEPARATOR###\n"
        combined_text = separator.join(texts)

        prompt = f"""请将以下文本翻译成{target_lang}。
文本之间使用"###TRANSLATE_SEPARATOR###"分隔。
请保持相同的分隔符，只翻译文本内容，不要添加任何解释。

原文：
{combined_text}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一个专业的翻译助手，擅长将各种语言翻译成{target_lang}。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            # 分割翻译结果
            translated_text = response.choices[0].message.content.strip()
            translated_list = translated_text.split(separator)

            # 确保返回的列表长度与输入一致
            if len(translated_list) != len(texts):
                # 如果数量不匹配，逐个翻译作为fallback
                return [self.translate_text(text, source_lang, target_lang) for text in texts]

            return translated_list
        except Exception as e:
            # 出错时fallback到逐个翻译
            print(f"批量翻译失败，使用逐个翻译: {str(e)}")
            return [self.translate_text(text, source_lang, target_lang) for text in texts]

    @retry_with_backoff()
    def describe_image(self, image_path: str, target_lang: str = "Chinese") -> str:
        """
        使用GPT-4o Vision描述图片内容

        Args:
            image_path: 图片路径
            target_lang: 描述语言

        Returns:
            图片描述文本
        """
        import base64

        # 读取并编码图片
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # 判断图片格式
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'
        else:
            mime_type = 'image/jpeg'

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"请用{target_lang}详细描述这张图片的内容，包括图片中的文字、场景、物体等所有信息。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"图片描述失败: {str(e)}")


# 创建全局客户端实例
ai_client = AIClient()
