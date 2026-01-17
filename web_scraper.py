"""
网页抓取模块
混合模式：requests + Selenium fallback
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import config
from utils.html_parser import html_parser
from folder_manager import FolderManager
import os


class WebScraper:
    """网页抓取器类"""

    def __init__(self):
        """初始化网页抓取器"""
        self.timeout = config.REQUEST_TIMEOUT
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def _needs_js_rendering(self, html: str) -> bool:
        """
        检测是否需要JavaScript渲染

        Args:
            html: HTML内容

        Returns:
            是否需要JS渲染
        """
        soup = BeautifulSoup(html, 'html.parser')

        # 检测常见的JS框架标识
        indicators = [
            soup.find('div', id='root'),  # React
            soup.find('div', id='app'),   # Vue
            soup.find(attrs={'ng-app': True}),  # Angular
        ]

        # 检测内容是否太少
        text_content = soup.get_text(strip=True)
        if len(text_content) < 100:
            return True

        return any(indicators)

    def fetch_with_requests(self, url: str) -> str:
        """
        使用requests获取网页

        Args:
            url: 网页URL

        Returns:
            HTML内容
        """
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text

    def fetch_with_selenium(self, url: str) -> str:
        """
        使用Selenium获取网页（headless模式）

        Args:
            url: 网页URL

        Returns:
            HTML内容
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')

        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            # 等待页面加载
            driver.implicitly_wait(5)
            html = driver.page_source
            return html
        finally:
            driver.quit()

    def fetch_page(self, url: str) -> str:
        """
        获取网页内容（自动选择模式）

        Args:
            url: 网页URL

        Returns:
            HTML内容
        """
        print(f"正在获取网页: {url}")

        try:
            # 先尝试requests
            html = self.fetch_with_requests(url)

            # 检测是否需要JS渲染
            if self._needs_js_rendering(html):
                print("检测到动态内容，切换到Selenium模式...")
                html = self.fetch_with_selenium(url)

            return html

        except Exception as e:
            # 失败时fallback到Selenium
            print(f"Requests失败，使用Selenium: {str(e)}")
            return self.fetch_with_selenium(url)

    def translate_and_save(self, url: str, source_lang: str = "auto",
                          target_lang: str = "Chinese", progress_callback=None) -> str:
        """
        翻译网页并保存

        Args:
            url: 网页URL
            source_lang: 源语言
            target_lang: 目标语言
            progress_callback: 进度回调

        Returns:
            保存的文件路径
        """
        # 获取网页内容
        html_content = self.fetch_page(url)

        # 翻译HTML
        print("正在翻译网页内容...")
        translated_html = html_parser.translate_html(
            html_content, source_lang, target_lang, progress_callback
        )

        # 保存翻译结果
        folder_manager = FolderManager(config.WEBPAGES_DIR)
        folder_path = folder_manager.create_folder()

        # 生成文件名
        filename = "translated_page.html"

        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(translated_html)

        # 保存原始URL
        url_file = os.path.join(folder_path, "original_url.txt")
        with open(url_file, 'w', encoding='utf-8') as f:
            f.write(url)

        print(f"翻译完成，保存至: {file_path}")
        return file_path


# 创建全局网页抓取器实例
web_scraper = WebScraper()
