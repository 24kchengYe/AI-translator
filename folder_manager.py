"""
文件夹管理模块
管理各个翻译场景的输出文件夹
"""
import os
import re
from pathlib import Path


class FolderManager:
    """文件夹管理器"""

    def __init__(self, base_dir: str):
        """
        初始化文件夹管理器

        Args:
            base_dir: 基础目录（webpages/words/documents/images）
        """
        self.base_dir = base_dir
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """确保基础目录存在"""
        os.makedirs(self.base_dir, exist_ok=True)

    def get_next_number(self) -> int:
        """
        获取下一个可用的编号

        Returns:
            下一个可用编号
        """
        if not os.path.exists(self.base_dir):
            return 1

        # 扫描现有文件夹，找到最大编号
        max_num = 0
        pattern = re.compile(r'translation(\d+)')

        for folder_name in os.listdir(self.base_dir):
            match = pattern.match(folder_name)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)

        return max_num + 1

    def create_folder(self, custom_name: str = None) -> str:
        """
        创建新的翻译文件夹

        Args:
            custom_name: 自定义文件夹名，如果为None则使用translation{N}

        Returns:
            创建的文件夹路径
        """
        if custom_name:
            folder_name = custom_name
        else:
            next_num = self.get_next_number()
            folder_name = f"translation{next_num}"

        folder_path = os.path.join(self.base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        return folder_path

    def save_file(self, content: str, filename: str, folder_name: str = None) -> str:
        """
        保存文件到指定文件夹

        Args:
            content: 文件内容
            filename: 文件名
            folder_name: 文件夹名，如果为None则创建新文件夹

        Returns:
            保存的文件路径
        """
        if folder_name:
            folder_path = os.path.join(self.base_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
        else:
            folder_path = self.create_folder()

        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    def list_folders(self) -> list:
        """
        列出所有翻译文件夹

        Returns:
            文件夹名列表
        """
        if not os.path.exists(self.base_dir):
            return []

        folders = []
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path):
                folders.append(item)

        return sorted(folders)
