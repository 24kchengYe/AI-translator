"""
HTML解析和翻译模块
批量优化HTML翻译
支持完整CSS样式和资源保留
"""
from bs4 import BeautifulSoup, NavigableString, Tag
from translation_engine import translation_engine
from config import config
from urllib.parse import urljoin, urlparse
import os


class HTMLParser:
    """HTML解析器类"""

    def __init__(self):
        """初始化HTML解析器"""
        self.batch_size = config.BATCH_SIZE
        # 不需要翻译的标签
        self.skip_tags = {'script', 'style', 'noscript', 'meta', 'link', 'head'}
        # 需要保留的属性（如alt、title）
        self.translate_attrs = {'alt', 'title', 'placeholder'}

    def extract_text_nodes(self, soup: BeautifulSoup) -> list:
        """
        提取HTML中所有需要翻译的文本节点

        Args:
            soup: BeautifulSoup对象

        Returns:
            文本节点列表，每个元素为(element, text)元组
        """
        text_nodes = []

        def traverse(element):
            """递归遍历元素"""
            if isinstance(element, NavigableString):
                # 文本节点
                text = str(element).strip()
                if text and element.parent.name not in self.skip_tags:
                    text_nodes.append((element, text))
            elif isinstance(element, Tag):
                # 标签节点
                if element.name in self.skip_tags:
                    return

                # 提取属性中的文本
                for attr in self.translate_attrs:
                    if attr in element.attrs and element[attr]:
                        text_nodes.append((element, element[attr], attr))

                # 遍历子节点
                for child in element.children:
                    traverse(child)

        traverse(soup)
        return text_nodes

    def preserve_resources(self, soup: BeautifulSoup, base_url: str = None):
        """
        保留完整的CSS样式和资源链接

        Args:
            soup: BeautifulSoup对象
            base_url: 网页基础URL（用于处理相对路径）
        """
        # 确保有base标签（方便浏览器解析相对路径）
        if base_url and not soup.find('base'):
            base_tag = soup.new_tag('base', href=base_url)
            if soup.head:
                soup.head.insert(0, base_tag)

        # 添加meta标签确保编码正确
        if soup.head:
            # 检查是否已有charset meta
            charset_meta = soup.find('meta', charset=True)
            if not charset_meta:
                charset_meta = soup.find('meta', attrs={'http-equiv': 'Content-Type'})

            if not charset_meta:
                meta_tag = soup.new_tag('meta', charset='utf-8')
                soup.head.insert(0, meta_tag)

        # 保留所有link标签（CSS样式表、图标等）
        # 无需修改，保持原样即可

        # 保留所有style标签（内联CSS）
        # 无需修改，保持原样即可

        # 如果需要将相对路径转为绝对路径（可选）
        if base_url:
            # 转换CSS链接
            for link in soup.find_all('link', href=True):
                if link.get('rel') and 'stylesheet' in link.get('rel'):
                    link['href'] = urljoin(base_url, link['href'])

            # 转换图片链接
            for img in soup.find_all('img', src=True):
                img['src'] = urljoin(base_url, img['src'])

            # 转换script链接
            for script in soup.find_all('script', src=True):
                script['src'] = urljoin(base_url, script['src'])

    def translate_html(self, html_content: str, source_lang: str = "auto",
                      target_lang: str = "Chinese", progress_callback=None,
                      base_url: str = None) -> str:
        """
        翻译HTML内容（批量优化，完整保留样式）

        Args:
            html_content: HTML内容
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调
            base_url: 网页基础URL（用于处理相对路径）

        Returns:
            翻译后的HTML内容
        """
        # 解析HTML，使用html.parser以保留完整结构
        soup = BeautifulSoup(html_content, 'html.parser')

        # 保留资源和样式
        self.preserve_resources(soup, base_url)

        # 提取所有文本节点
        text_nodes = self.extract_text_nodes(soup)

        if not text_nodes:
            return str(soup)

        # 提取文本内容
        texts = []
        for node_info in text_nodes:
            if len(node_info) == 2:
                # 普通文本节点
                texts.append(node_info[1])
            else:
                # 属性文本
                texts.append(node_info[1])

        # 批量翻译
        print(f"正在翻译 {len(texts)} 个文本节点...")
        translated_texts = translation_engine.translate_batch(
            texts, source_lang, target_lang, progress_callback
        )

        # 替换翻译后的文本
        for i, node_info in enumerate(text_nodes):
            if i < len(translated_texts):
                if len(node_info) == 2:
                    # 普通文本节点
                    element, original_text = node_info
                    element.replace_with(NavigableString(translated_texts[i]))
                else:
                    # 属性文本
                    element, original_text, attr = node_info
                    element[attr] = translated_texts[i]

        # 返回翻译后的HTML（使用prettify保持格式）
        return str(soup)

    def translate_html_simple(self, html_content: str, source_lang: str = "auto",
                             target_lang: str = "Chinese") -> str:
        """
        简单翻译HTML（直接翻译所有可见文本）

        Args:
            html_content: HTML内容
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译后的HTML内容
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除script和style标签
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        # 获取所有文本
        text = soup.get_text(separator='\n', strip=True)

        # 翻译
        translated_text = translation_engine.translate(text, source_lang, target_lang)

        return translated_text


# 创建全局HTML解析器实例
html_parser = HTMLParser()
