"""
文档处理模块
支持PDF和Word文档，转换为Markdown输出
"""
import os
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document
from translation_engine import translation_engine
from folder_manager import FolderManager
from config import config


class DocumentProcessor:
    """文档处理器类"""

    def __init__(self):
        """初始化文档处理器"""
        pass

    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        从PDF提取文本（pdfplumber优先，PyPDF2 fallback）

        Args:
            pdf_path: PDF文件路径

        Returns:
            提取的文本
        """
        text_parts = []

        try:
            # 优先使用pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"## Page {page_num}\n\n{text}\n")

            if text_parts:
                return '\n'.join(text_parts)

        except Exception as e:
            print(f"pdfplumber失败，使用PyPDF2: {str(e)}")

        # Fallback到PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"## Page {page_num}\n\n{text}\n")

            return '\n'.join(text_parts)

        except Exception as e:
            raise Exception(f"PDF文本提取失败: {str(e)}")

    def extract_docx_text(self, docx_path: str) -> str:
        """
        从Word文档提取文本

        Args:
            docx_path: Word文档路径

        Returns:
            提取的文本（Markdown格式）
        """
        doc = Document(docx_path)
        text_parts = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                # 根据样式判断标题级别
                if paragraph.style.name.startswith('Heading'):
                    level = paragraph.style.name[-1]
                    if level.isdigit():
                        text_parts.append(f"{'#' * int(level)} {text}\n")
                    else:
                        text_parts.append(f"## {text}\n")
                else:
                    text_parts.append(f"{text}\n")

        return '\n'.join(text_parts)

    def split_into_chunks(self, text: str, chunk_size: int = 2000) -> list:
        """
        将长文本分割成小块

        Args:
            text: 文本内容
            chunk_size: 每块的最大字符数

        Returns:
            文本块列表
        """
        # 按段落分割
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_size and current_chunk:
                # 当前块已满，保存并开始新块
                chunks.append('\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        # 添加最后一块
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def translate_document(self, file_path: str, source_lang: str = "auto",
                          target_lang: str = "Chinese", progress_callback=None) -> str:
        """
        翻译文档并保存为Markdown

        Args:
            file_path: 文档路径
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调

        Returns:
            保存的文件路径
        """
        file_ext = Path(file_path).suffix.lower()

        # 提取文本
        print(f"正在提取文档内容: {file_path}")
        if file_ext == '.pdf':
            text = self.extract_pdf_text(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = self.extract_docx_text(file_path)
        else:
            raise ValueError(f"不支持的文档格式: {file_ext}")

        # 分割成块
        chunks = self.split_into_chunks(text, chunk_size=2000)
        print(f"文档分为 {len(chunks)} 个部分进行翻译")

        # 翻译每个块
        translated_chunks = []
        for i, chunk in enumerate(chunks, 1):
            if progress_callback:
                progress_callback(i, len(chunks))

            print(f"正在翻译第 {i}/{len(chunks)} 部分...")
            translated = translation_engine.translate(chunk, source_lang, target_lang)
            translated_chunks.append(translated)

        # 合并翻译结果
        translated_text = '\n\n'.join(translated_chunks)

        # 保存为Markdown
        folder_manager = FolderManager(config.DOCUMENTS_DIR)
        folder_path = folder_manager.create_folder()

        original_name = Path(file_path).stem
        output_file = os.path.join(folder_path, f"{original_name}_translated.md")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 翻译文档: {original_name}\n\n")
            f.write(f"**原文件**: {Path(file_path).name}\n\n")
            f.write(f"**翻译语言**: {target_lang}\n\n")
            f.write("---\n\n")
            f.write(translated_text)

        # 保存原始文件信息
        info_file = os.path.join(folder_path, "document_info.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"原始文件: {file_path}\n")
            f.write(f"文件名: {Path(file_path).name}\n")
            f.write(f"翻译语言: {target_lang}\n")

        print(f"翻译完成，保存至: {output_file}")
        return output_file


# 创建全局文档处理器实例
document_processor = DocumentProcessor()
