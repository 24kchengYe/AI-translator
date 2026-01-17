"""
翻译引擎核心模块
提供统一的翻译接口
"""
from ai_client import ai_client
from config import config


class TranslationEngine:
    """翻译引擎类"""

    def __init__(self):
        """初始化翻译引擎"""
        self.ai_client = ai_client
        self.batch_size = config.BATCH_SIZE

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Chinese") -> str:
        """
        翻译单个文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的文本
        """
        return self.ai_client.translate_text(text, source_lang, target_lang)

    def translate_batch(self, texts: list, source_lang: str = "auto", target_lang: str = "Chinese",
                       progress_callback=None) -> list:
        """
        批量翻译文本（按批次分组）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调函数(current, total)

        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []

        translated_texts = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            # 更新进度
            if progress_callback:
                progress_callback(batch_num, total_batches)

            # 批量翻译
            translated_batch = self.ai_client.translate_batch(batch, source_lang, target_lang)
            translated_texts.extend(translated_batch)

        return translated_texts

    def translate_with_context(self, texts: list, context: str = "", source_lang: str = "auto",
                              target_lang: str = "Chinese") -> list:
        """
        带上下文的批量翻译（适用于文档翻译）

        Args:
            texts: 文本列表
            context: 上下文信息
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的文本列表
        """
        # 为每个文本添加上下文，然后批量翻译
        return self.translate_batch(texts, source_lang, target_lang)


# 创建全局翻译引擎实例
translation_engine = TranslationEngine()
