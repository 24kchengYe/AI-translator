"""
翻译引擎核心模块
提供统一的翻译接口
"""
from ai_client import ai_client
from config import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import asyncio


class TranslationEngine:
    """翻译引擎类"""

    def __init__(self):
        """初始化翻译引擎"""
        self.ai_client = ai_client
        self.batch_size = config.BATCH_SIZE
        # 并发配置
        self.max_workers = config.MAX_WORKERS
        self.parallel_enabled = config.PARALLEL_ENABLED

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
                       progress_callback=None, parallel: bool = True) -> list:
        """
        批量翻译文本（支持并行处理）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调函数(current, total)
            parallel: 是否启用并行翻译（默认True）

        Returns:
            翻译后的文本列表
        """
        if not texts:
            return []

        # 检查是否启用并行
        if not parallel or not self.parallel_enabled:
            return self._translate_batch_serial(texts, source_lang, target_lang, progress_callback)

        # 小批次直接串行处理（并行开销大于收益）
        if len(texts) <= 10:
            return self._translate_batch_serial(texts, source_lang, target_lang, progress_callback)

        # 大批次优先使用异步IO并行处理（性能更好）
        try:
            return self._translate_batch_async(texts, source_lang, target_lang, progress_callback)
        except Exception as e:
            print(f"异步翻译失败，降级到线程池并行: {str(e)}")
            return self._translate_batch_parallel(texts, source_lang, target_lang, progress_callback)

    def _translate_batch_serial(self, texts: list, source_lang: str, target_lang: str,
                                progress_callback=None) -> list:
        """
        串行批量翻译（原始实现）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调函数(current, total)

        Returns:
            翻译后的文本列表
        """
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

    def _translate_batch_parallel(self, texts: list, source_lang: str, target_lang: str,
                                  progress_callback=None) -> list:
        """
        并行批量翻译（优化性能）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调函数(current, total)

        Returns:
            翻译后的文本列表
        """
        # 计算批次
        total_batches = math.ceil(len(texts) / self.batch_size)

        # 动态调整并发数：根据批次数量和最大并发数取最小值
        workers = min(self.max_workers, total_batches)

        # 创建批次任务
        batches = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_index = i // self.batch_size
            batches.append((batch_index, batch))

        # 存储翻译结果（按批次索引）
        results = {}
        completed = 0

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任务
            future_to_batch = {
                executor.submit(self.ai_client.translate_batch, batch, source_lang, target_lang): (batch_idx, batch)
                for batch_idx, batch in batches
            }

            # 处理完成的任务
            for future in as_completed(future_to_batch):
                batch_idx, batch = future_to_batch[future]
                try:
                    translated_batch = future.result()
                    results[batch_idx] = translated_batch
                    completed += 1

                    # 更新进度
                    if progress_callback:
                        progress_callback(completed, total_batches)

                except Exception as e:
                    print(f"批次 {batch_idx} 翻译失败: {str(e)}")
                    # 失败时使用逐个翻译作为fallback
                    fallback_results = []
                    for text in batch:
                        try:
                            fallback_results.append(self.ai_client.translate_text(text, source_lang, target_lang))
                        except:
                            fallback_results.append(text)  # 保留原文
                    results[batch_idx] = fallback_results

        # 按顺序合并结果
        translated_texts = []
        for i in range(total_batches):
            if i in results:
                translated_texts.extend(results[i])

        return translated_texts

    def _translate_batch_async(self, texts: list, source_lang: str, target_lang: str,
                               progress_callback=None) -> list:
        """
        异步IO并行翻译（最高性能）

        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调函数(current, total)

        Returns:
            翻译后的文本列表
        """
        from ai_client_async import async_ai_client

        # 计算批次
        total_batches = math.ceil(len(texts) / self.batch_size)

        # 创建批次任务
        batches = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_index = i // self.batch_size
            batches.append((batch_index, batch))

        async def translate_all_batches():
            """异步翻译所有批次"""
            # 使用信号量限制并发数
            semaphore = asyncio.Semaphore(self.max_workers)
            results = {}
            completed = [0]  # 使用列表以便在内部函数中修改

            async def translate_with_semaphore(batch_idx, batch):
                """带信号量控制的翻译"""
                async with semaphore:
                    try:
                        result = await async_ai_client.translate_batch_async(batch, source_lang, target_lang)
                        results[batch_idx] = result
                        completed[0] += 1

                        # 更新进度
                        if progress_callback:
                            progress_callback(completed[0], total_batches)

                        return result
                    except Exception as e:
                        print(f"批次 {batch_idx} 异步翻译失败: {str(e)}")
                        # 失败时使用同步客户端fallback
                        fallback_results = []
                        for text in batch:
                            try:
                                fallback_results.append(ai_client.translate_text(text, source_lang, target_lang))
                            except:
                                fallback_results.append(text)
                        results[batch_idx] = fallback_results
                        completed[0] += 1
                        if progress_callback:
                            progress_callback(completed[0], total_batches)
                        return fallback_results

            # 创建所有任务
            tasks = [translate_with_semaphore(batch_idx, batch) for batch_idx, batch in batches]

            # 并发执行所有任务
            await asyncio.gather(*tasks)

            return results

        # 运行异步事件循环
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建新线程运行
                import threading
                result_container = [None]
                error_container = [None]

                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result_container[0] = new_loop.run_until_complete(translate_all_batches())
                        new_loop.close()
                    except Exception as e:
                        error_container[0] = e

                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

                if error_container[0]:
                    raise error_container[0]
                batch_results = result_container[0]
            else:
                # 直接运行
                batch_results = loop.run_until_complete(translate_all_batches())
        except RuntimeError:
            # 没有事件循环，创建新的
            batch_results = asyncio.run(translate_all_batches())

        # 按顺序合并结果
        translated_texts = []
        for i in range(total_batches):
            if i in batch_results:
                translated_texts.extend(batch_results[i])

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
