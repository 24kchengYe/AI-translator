"""
主窗口GUI
使用CustomTkinter实现苹果极简风格界面
"""
import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import os
import webbrowser
from pathlib import Path


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 窗口配置
        self.title("AI翻译助手")
        self.geometry("900x700")

        # 设置主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 设置全局字体为非衬线体
        self.default_font = ctk.CTkFont(family="Arial", size=12)
        self.title_font = ctk.CTkFont(family="Arial", size=24, weight="bold")
        self.heading_font = ctk.CTkFont(family="Arial", size=14, weight="bold")
        self.text_font = ctk.CTkFont(family="Arial", size=13)

        # 语言选项
        self.languages = {
            "中文": "Chinese",
            "英文": "English",
            "日文": "Japanese",
            "韩文": "Korean",
            "法文": "French",
            "德文": "German",
            "西班牙文": "Spanish",
            "俄文": "Russian"
        }

        # 任务队列
        self.task_queue = queue.Queue()

        # 创建UI
        self.create_widgets()

        # 启动队列检查
        self.check_queue()

    def create_widgets(self):
        """创建UI组件"""
        # 顶部区域
        self.create_header()

        # 中间Tab区域
        self.create_tabs()

        # 底部状态栏
        self.create_status_bar()

    def create_header(self):
        """创建顶部区域"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="AI翻译助手",
            font=self.title_font
        )
        title_label.pack(side="left")

        # 语言选择
        lang_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        lang_frame.pack(side="right")

        ctk.CTkLabel(lang_frame, text="目标语言:", font=self.default_font).pack(side="left", padx=(0, 10))

        self.target_lang_var = ctk.StringVar(value="中文")
        self.target_lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=list(self.languages.keys()),
            variable=self.target_lang_var,
            width=120,
            font=self.default_font
        )
        self.target_lang_menu.pack(side="left")

    def create_tabs(self):
        """创建Tab区域"""
        # Tab容器
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加四个Tab
        self.tab_webpage = self.tabview.add("网页翻译")
        self.tab_text = self.tabview.add("文本翻译")
        self.tab_document = self.tabview.add("文档翻译")
        self.tab_image = self.tabview.add("图片翻译")

        # 填充各个Tab
        self.create_webpage_tab()
        self.create_text_tab()
        self.create_document_tab()
        self.create_image_tab()

    def create_webpage_tab(self):
        """创建网页翻译Tab"""
        # 提示
        tip_label = ctk.CTkLabel(
            self.tab_webpage,
            text="每行输入一个网页链接",
            font=self.default_font
        )
        tip_label.pack(pady=(10, 5))

        # URL输入框
        self.url_textbox = ctk.CTkTextbox(
            self.tab_webpage,
            height=400,
            font=self.text_font
        )
        self.url_textbox.pack(fill="both", expand=True, padx=20, pady=10)

        # 翻译按钮
        self.webpage_btn = ctk.CTkButton(
            self.tab_webpage,
            text="开始翻译",
            command=self.translate_webpage,
            height=40,
            font=self.heading_font
        )
        self.webpage_btn.pack(pady=10)

    def create_text_tab(self):
        """创建文本翻译Tab"""
        # 输入区域
        input_frame = ctk.CTkFrame(self.tab_text)
        input_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            input_frame,
            text="输入文本",
            font=self.default_font
        ).pack(anchor="w", pady=(5, 5))

        self.text_input = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=self.text_font
        )
        self.text_input.pack(fill="both", expand=True)

        # 翻译按钮
        self.text_btn = ctk.CTkButton(
            self.tab_text,
            text="翻译",
            command=self.translate_text,
            height=40,
            font=self.heading_font
        )
        self.text_btn.pack(pady=10)

        # 输出区域
        output_frame = ctk.CTkFrame(self.tab_text)
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            output_frame,
            text="翻译结果",
            font=self.default_font
        ).pack(anchor="w", pady=(5, 5))

        self.text_output = ctk.CTkTextbox(
            output_frame,
            height=150,
            font=self.text_font
        )
        self.text_output.pack(fill="both", expand=True)

    def create_document_tab(self):
        """创建文档翻译Tab"""
        # 拖拽区域
        drop_frame = ctk.CTkFrame(
            self.tab_document,
            border_width=2,
            border_color="#007AFF"
        )
        drop_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # 提示信息
        ctk.CTkLabel(
            drop_frame,
            text="📄",
            font=ctk.CTkFont(family="Arial", size=48)
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            drop_frame,
            text="拖拽PDF/Word文件到此处",
            font=ctk.CTkFont(family="Arial", size=16)
        ).pack()

        ctk.CTkLabel(
            drop_frame,
            text="或点击下方按钮选择文件",
            font=self.default_font,
            text_color="gray"
        ).pack(pady=5)

        # 已选文件标签
        self.doc_file_label = ctk.CTkLabel(
            drop_frame,
            text="",
            font=self.default_font,
            text_color="#007AFF"
        )
        self.doc_file_label.pack(pady=10)

        # 按钮区域
        btn_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 40))

        self.doc_select_btn = ctk.CTkButton(
            btn_frame,
            text="选择文件",
            command=self.select_document,
            width=120,
            font=self.default_font
        )
        self.doc_select_btn.pack(side="left", padx=5)

        self.doc_translate_btn = ctk.CTkButton(
            btn_frame,
            text="开始翻译",
            command=self.translate_document,
            width=120,
            state="disabled",
            font=self.default_font
        )
        self.doc_translate_btn.pack(side="left", padx=5)

        self.selected_doc_path = None

    def create_image_tab(self):
        """创建图片翻译Tab"""
        # 拖拽区域
        drop_frame = ctk.CTkFrame(
            self.tab_image,
            border_width=2,
            border_color="#007AFF"
        )
        drop_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # 提示信息
        ctk.CTkLabel(
            drop_frame,
            text="🖼️",
            font=ctk.CTkFont(family="Arial", size=48)
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            drop_frame,
            text="拖拽图片文件到此处",
            font=ctk.CTkFont(family="Arial", size=16)
        ).pack()

        ctk.CTkLabel(
            drop_frame,
            text="或点击下方按钮选择图片",
            font=self.default_font,
            text_color="gray"
        ).pack(pady=5)

        # 已选文件标签
        self.img_file_label = ctk.CTkLabel(
            drop_frame,
            text="",
            font=self.default_font,
            text_color="#007AFF"
        )
        self.img_file_label.pack(pady=10)

        # 按钮区域
        btn_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 40))

        self.img_select_btn = ctk.CTkButton(
            btn_frame,
            text="选择图片",
            command=self.select_image,
            width=120,
            font=self.default_font
        )
        self.img_select_btn.pack(side="left", padx=5)

        self.img_translate_btn = ctk.CTkButton(
            btn_frame,
            text="开始描述",
            command=self.translate_image,
            width=120,
            state="disabled",
            font=self.default_font
        )
        self.img_translate_btn.pack(side="left", padx=5)

        self.selected_img_path = None

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ctk.CTkFrame(self, height=80)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        # 状态消息
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=self.default_font
        )
        self.status_label.pack(pady=(0, 15))

    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """
        显示消息弹窗（使用Arial字体）

        Args:
            title: 标题
            message: 消息内容
            msg_type: 消息类型 (info/warning/error)
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)

        # 居中显示
        dialog.transient(self)
        dialog.grab_set()

        # 消息内容
        msg_label = ctk.CTkLabel(
            dialog,
            text=message,
            font=self.default_font,
            wraplength=350
        )
        msg_label.pack(pady=30, padx=20)

        # 确定按钮
        ok_btn = ctk.CTkButton(
            dialog,
            text="确定",
            command=dialog.destroy,
            width=100,
            font=self.default_font
        )
        ok_btn.pack(pady=20)

        # 等待窗口关闭
        self.wait_window(dialog)

    def show_yes_no(self, title: str, message: str) -> bool:
        """
        显示是/否确认弹窗（使用Arial字体）

        Args:
            title: 标题
            message: 消息内容

        Returns:
            True: 用户点击"是"，False: 用户点击"否"
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)

        # 居中显示
        dialog.transient(self)
        dialog.grab_set()

        # 用于保存用户选择
        result = [False]

        # 消息内容
        msg_label = ctk.CTkLabel(
            dialog,
            text=message,
            font=self.default_font,
            wraplength=350
        )
        msg_label.pack(pady=30, padx=20)

        # 按钮区域
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        def on_yes():
            result[0] = True
            dialog.destroy()

        def on_no():
            result[0] = False
            dialog.destroy()

        yes_btn = ctk.CTkButton(
            btn_frame,
            text="是",
            command=on_yes,
            width=80,
            font=self.default_font
        )
        yes_btn.pack(side="left", padx=10)

        no_btn = ctk.CTkButton(
            btn_frame,
            text="否",
            command=on_no,
            width=80,
            font=self.default_font
        )
        no_btn.pack(side="left", padx=10)

        # 等待窗口关闭
        self.wait_window(dialog)

        return result[0]

    def update_status(self, message: str, progress: float = None):
        """更新状态"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)

    def get_target_language(self) -> str:
        """获取目标语言"""
        lang_name = self.target_lang_var.get()
        return self.languages.get(lang_name, "Chinese")

    def translate_webpage(self):
        """翻译网页"""
        urls_text = self.url_textbox.get("1.0", "end").strip()
        if not urls_text:
            self.show_message("警告", "请输入至少一个网页URL", "warning")
            return

        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        target_lang = self.get_target_language()

        # 禁用按钮
        self.webpage_btn.configure(state="disabled")

        # 启动后台线程
        thread = threading.Thread(
            target=self._translate_webpage_worker,
            args=(urls, target_lang),
            daemon=True
        )
        thread.start()

    def _translate_webpage_worker(self, urls: list, target_lang: str):
        """网页翻译工作线程"""
        from web_scraper import web_scraper

        try:
            results = []
            for i, url in enumerate(urls, 1):
                self.task_queue.put(("status", f"正在翻译网页 {i}/{len(urls)}: {url}", i/len(urls)))

                def progress_callback(current, total):
                    self.task_queue.put(("status", f"翻译进度: {current}/{total}", None))

                try:
                    result = web_scraper.translate_and_save(url, target_lang=target_lang, progress_callback=progress_callback)
                    results.append(result)
                except Exception as e:
                    self.task_queue.put(("error", f"翻译失败 {url}: {str(e)}"))

            # 完成
            self.task_queue.put(("webpage_complete", results))

        except Exception as e:
            self.task_queue.put(("error", f"翻译失败: {str(e)}"))

    def translate_text(self):
        """翻译文本"""
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            self.show_message("警告", "请输入要翻译的文本", "warning")
            return

        target_lang = self.get_target_language()

        # 禁用按钮
        self.text_btn.configure(state="disabled")

        # 启动后台线程
        thread = threading.Thread(
            target=self._translate_text_worker,
            args=(text, target_lang),
            daemon=True
        )
        thread.start()

    def _translate_text_worker(self, text: str, target_lang: str):
        """文本翻译工作线程"""
        from translation_engine import translation_engine
        from folder_manager import FolderManager
        from config import config

        try:
            self.task_queue.put(("status", "正在翻译...", 0.5))

            # 翻译
            translated = translation_engine.translate(text, target_lang=target_lang)

            # 保存
            folder_manager = FolderManager(config.WORDS_DIR)
            file_path = folder_manager.save_file(
                f"原文:\n{text}\n\n{'='*50}\n\n翻译:\n{translated}",
                "translation.txt"
            )

            self.task_queue.put(("text_complete", translated, file_path))

        except Exception as e:
            self.task_queue.put(("error", f"翻译失败: {str(e)}"))

    def select_document(self):
        """选择文档"""
        file_path = filedialog.askopenfilename(
            title="选择文档",
            filetypes=[
                ("文档文件", "*.pdf *.docx *.doc"),
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.docx *.doc"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.selected_doc_path = file_path
            self.doc_file_label.configure(text=f"已选择: {Path(file_path).name}")
            self.doc_translate_btn.configure(state="normal")

    def translate_document(self):
        """翻译文档"""
        if not self.selected_doc_path:
            self.show_message("警告", "请先选择文档", "warning")
            return

        target_lang = self.get_target_language()

        # 禁用按钮
        self.doc_translate_btn.configure(state="disabled")
        self.doc_select_btn.configure(state="disabled")

        # 启动后台线程
        thread = threading.Thread(
            target=self._translate_document_worker,
            args=(self.selected_doc_path, target_lang),
            daemon=True
        )
        thread.start()

    def _translate_document_worker(self, file_path: str, target_lang: str):
        """文档翻译工作线程"""
        from document_processor import document_processor

        try:
            def progress_callback(current, total):
                self.task_queue.put(("status", f"翻译进度: {current}/{total}", current/total))

            self.task_queue.put(("status", "正在处理文档...", 0.1))

            result = document_processor.translate_document(
                file_path,
                target_lang=target_lang,
                progress_callback=progress_callback
            )

            self.task_queue.put(("document_complete", result))

        except Exception as e:
            self.task_queue.put(("error", f"翻译失败: {str(e)}"))

    def select_image(self):
        """选择图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.selected_img_path = file_path
            self.img_file_label.configure(text=f"已选择: {Path(file_path).name}")
            self.img_translate_btn.configure(state="normal")

    def translate_image(self):
        """翻译图片"""
        if not self.selected_img_path:
            self.show_message("警告", "请先选择图片", "warning")
            return

        target_lang = self.get_target_language()

        # 禁用按钮
        self.img_translate_btn.configure(state="disabled")
        self.img_select_btn.configure(state="disabled")

        # 启动后台线程
        thread = threading.Thread(
            target=self._translate_image_worker,
            args=(self.selected_img_path, target_lang),
            daemon=True
        )
        thread.start()

    def _translate_image_worker(self, image_path: str, target_lang: str):
        """图片翻译工作线程"""
        from image_processor import image_processor

        try:
            self.task_queue.put(("status", "正在分析图片...", 0.5))

            result = image_processor.describe_and_save(image_path, target_lang)

            self.task_queue.put(("image_complete", result))

        except Exception as e:
            self.task_queue.put(("error", f"处理失败: {str(e)}"))

    def check_queue(self):
        """检查任务队列"""
        try:
            while True:
                msg = self.task_queue.get_nowait()

                if msg[0] == "status":
                    _, text, progress = msg
                    self.update_status(text, progress)

                elif msg[0] == "error":
                    _, error_msg = msg
                    self.update_status("错误", 0)
                    self.show_message("错误", error_msg, "error")
                    self._enable_all_buttons()

                elif msg[0] == "webpage_complete":
                    _, results = msg
                    self.update_status(f"完成！翻译了 {len(results)} 个网页", 1.0)
                    self.show_message("完成", f"成功翻译 {len(results)} 个网页\n\n文件保存在 webpages/ 文件夹")
                    self.webpage_btn.configure(state="normal")

                elif msg[0] == "text_complete":
                    _, translated, file_path = msg
                    self.text_output.delete("1.0", "end")
                    self.text_output.insert("1.0", translated)
                    self.update_status("翻译完成", 1.0)
                    self.show_message("完成", f"翻译完成\n\n保存至: {file_path}")
                    self.text_btn.configure(state="normal")

                elif msg[0] == "document_complete":
                    _, result = msg
                    self.update_status("翻译完成", 1.0)
                    should_open = self.show_yes_no("完成", f"文档翻译完成\n\n保存至: {result}\n\n是否打开文件？")
                    if should_open:
                        os.startfile(msg[1])
                    self._enable_document_buttons()

                elif msg[0] == "image_complete":
                    _, result = msg
                    self.update_status("处理完成", 1.0)
                    should_open = self.show_yes_no("完成", f"图片描述完成\n\n保存至: {result}\n\n是否打开文件？")
                    if should_open:
                        os.startfile(msg[1])
                    self._enable_image_buttons()

        except queue.Empty:
            pass

        # 每100ms检查一次
        self.after(100, self.check_queue)

    def _enable_all_buttons(self):
        """启用所有按钮"""
        self.webpage_btn.configure(state="normal")
        self.text_btn.configure(state="normal")
        self._enable_document_buttons()
        self._enable_image_buttons()

    def _enable_document_buttons(self):
        """启用文档按钮"""
        self.doc_select_btn.configure(state="normal")
        if self.selected_doc_path:
            self.doc_translate_btn.configure(state="normal")

    def _enable_image_buttons(self):
        """启用图片按钮"""
        self.img_select_btn.configure(state="normal")
        if self.selected_img_path:
            self.img_translate_btn.configure(state="normal")


def run_gui():
    """运行GUI"""
    app = MainWindow()
    app.mainloop()
