"""
图片处理模块
使用GPT-4o Vision描述图片内容
"""
import os
from pathlib import Path
from PIL import Image
from ai_client import ai_client
from folder_manager import FolderManager
from config import config


class ImageProcessor:
    """图片处理器类"""

    def __init__(self):
        """初始化图片处理器"""
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

    def validate_image(self, image_path: str) -> bool:
        """
        验证图片文件

        Args:
            image_path: 图片路径

        Returns:
            是否为有效图片
        """
        if not os.path.exists(image_path):
            return False

        file_ext = Path(image_path).suffix.lower()
        if file_ext not in self.supported_formats:
            return False

        try:
            # 尝试打开图片
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def get_image_info(self, image_path: str) -> dict:
        """
        获取图片信息

        Args:
            image_path: 图片路径

        Returns:
            图片信息字典
        """
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }

    def describe_and_save(self, image_path: str, target_lang: str = "Chinese") -> str:
        """
        描述图片并保存结果

        Args:
            image_path: 图片路径
            target_lang: 描述语言

        Returns:
            保存的文件路径
        """
        # 验证图片
        if not self.validate_image(image_path):
            raise ValueError(f"无效的图片文件: {image_path}")

        # 获取图片信息
        info = self.get_image_info(image_path)
        print(f"正在处理图片: {Path(image_path).name}")
        print(f"图片尺寸: {info['width']}x{info['height']}, 格式: {info['format']}")

        # 使用GPT-4o Vision描述图片
        print("正在生成图片描述...")
        description = ai_client.describe_image(image_path, target_lang)

        # 保存结果
        folder_manager = FolderManager(config.IMAGES_DIR)
        folder_path = folder_manager.create_folder()

        # 复制图片到输出文件夹
        original_name = Path(image_path).name
        image_copy_path = os.path.join(folder_path, original_name)

        with Image.open(image_path) as img:
            img.save(image_copy_path)

        # 保存描述文本
        desc_file = os.path.join(folder_path, f"{Path(image_path).stem}_description.txt")
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(f"图片文件: {original_name}\n")
            f.write(f"图片尺寸: {info['width']}x{info['height']}\n")
            f.write(f"图片格式: {info['format']}\n")
            f.write(f"描述语言: {target_lang}\n")
            f.write("\n" + "="*50 + "\n\n")
            f.write("图片描述:\n\n")
            f.write(description)

        # 保存为Markdown格式
        md_file = os.path.join(folder_path, f"{Path(image_path).stem}_description.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 图片描述: {original_name}\n\n")
            f.write(f"![{original_name}]({original_name})\n\n")
            f.write(f"**尺寸**: {info['width']}x{info['height']}\n\n")
            f.write(f"**格式**: {info['format']}\n\n")
            f.write("---\n\n")
            f.write("## 描述内容\n\n")
            f.write(description)

        # 保存原始文件信息
        info_file = os.path.join(folder_path, "image_info.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"原始路径: {image_path}\n")
            f.write(f"文件名: {original_name}\n")
            f.write(f"描述语言: {target_lang}\n")

        print(f"处理完成，保存至: {md_file}")
        return md_file

    def batch_describe(self, image_paths: list, target_lang: str = "Chinese",
                      progress_callback=None) -> list:
        """
        批量描述图片

        Args:
            image_paths: 图片路径列表
            target_lang: 描述语言
            progress_callback: 进度回调

        Returns:
            保存文件路径列表
        """
        results = []

        for i, image_path in enumerate(image_paths, 1):
            if progress_callback:
                progress_callback(i, len(image_paths))

            try:
                result = self.describe_and_save(image_path, target_lang)
                results.append(result)
            except Exception as e:
                print(f"处理失败 {image_path}: {str(e)}")
                results.append(None)

        return results


# 创建全局图片处理器实例
image_processor = ImageProcessor()
