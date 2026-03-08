\![Visitors](https://visitor-badge.laobi.icu/badge?page_id=24kchengYe.AI-translator)
# AI翻译助手

基于AI API的多场景翻译软件，支持网页、文本、文档和图片翻译。

## 功能特点

- **网页翻译**: 支持静态和动态网页，批量URL翻译
- **文本翻译**: 实时文本翻译，支持长文本
- **文档翻译**: PDF/Word转Markdown格式输出
- **图片翻译**: GPT-4o Vision图片内容描述
- **苹果极简风格**: CustomTkinter现代化界面
- **批量优化**: 智能批处理减少95%的API调用
- **自动重试**: 网络失败自动重试机制

## 安装步骤

### 1. 克隆或下载项目

```bash
cd 工具开发/050翻译软件
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

1. 复制配置模板:
```bash
copy .env.example .env
```

2. 编辑`.env`文件，填入你的OpenRouter API密钥:
```env
OPENAI_API_KEY=your_actual_api_key_here
```

获取API密钥: https://openrouter.ai/

## 使用方法

### 启动程序

```bash
python main.py
```

### 使用界面

#### 1. 网页翻译
- 在文本框中输入URL（每行一个）
- 选择目标语言
- 点击"开始翻译"
- 翻译结果保存在 `webpages/translation{N}/` 文件夹

#### 2. 文本翻译
- 在输入框输入文本
- 选择目标语言
- 点击"翻译"
- 结果显示在输出框，同时保存在 `words/translation{N}/` 文件夹

#### 3. 文档翻译
- 点击"选择文件"或拖拽文件到虚线框
- 支持格式: PDF, DOCX, DOC
- 点击"开始翻译"
- Markdown格式结果保存在 `documents/translation{N}/` 文件夹

#### 4. 图片翻译
- 点击"选择图片"或拖拽文件到虚线框
- 支持格式: PNG, JPG, JPEG, GIF, BMP
- 点击"开始描述"
- 描述保存在 `images/translation{N}/` 文件夹

## 项目结构

```
050翻译软件/
├── main.py                      # 主程序入口
├── .env                         # API配置（需要创建）
├── .env.example                 # 配置模板
├── requirements.txt             # 依赖清单
├── README.md                    # 使用说明
├── config.py                    # 配置管理
├── ai_client.py                 # AI API客户端
├── folder_manager.py            # 文件夹管理
├── translation_engine.py        # 翻译核心引擎
├── web_scraper.py              # 网页抓取
├── document_processor.py       # 文档处理
├── image_processor.py          # 图片处理
├── utils/                       # 工具模块
│   ├── retry_decorator.py      # 重试装饰器
│   └── html_parser.py          # HTML解析
├── gui/                         # GUI模块
│   └── main_window.py          # 主窗口
├── webpages/                    # 网页翻译输出
├── words/                       # 文本翻译输出
├── documents/                   # 文档翻译输出
└── images/                      # 图片翻译输出
```

## 核心技术

### HTML批量翻译优化
- 提取所有文本节点
- 每25个节点合并为一次API调用
- 完整保留HTML结构和样式
- 减少95%的API调用次数

### 混合网页抓取
- 默认使用requests（快速）
- 自动检测动态内容（React/Vue/Angular）
- 需要时自动切换到Selenium渲染
- 失败自动fallback

### 文档转Markdown
- PDF: pdfplumber → PyPDF2 fallback
- Word: 保留标题层级结构
- 长文本智能分块翻译

### 图片处理
- GPT-4o Vision多模态分析
- 完整描述图片中的文字和场景
- 同时保存图片副本和描述文本

## 配置说明

`.env`文件配置项:

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | OpenRouter API密钥 | 必填 |
| OPENAI_BASE_URL | API端点 | https://openrouter.ai/api/v1 |
| OPENAI_MODEL | 使用的模型 | openai/gpt-4o |
| BATCH_SIZE | 批处理大小 | 25 |
| MAX_RETRIES | 最大重试次数 | 3 |
| RETRY_DELAY | 重试延迟（秒） | 5 |
| REQUEST_TIMEOUT | 请求超时（秒） | 10 |

## 常见问题

### 1. 启动失败
- 检查是否安装了所有依赖
- 检查`.env`文件是否存在且配置正确
- 检查API密钥是否有效

### 2. 网页翻译失败
- 检查URL格式是否正确
- 检查网络连接
- 某些网站可能需要较长加载时间

### 3. 文档翻译慢
- 大文档会自动分块翻译
- 每个块需要单独的API调用
- 可以调整`BATCH_SIZE`参数

### 4. ChromeDriver错误
- 程序会自动下载ChromeDriver
- 如果失败，请手动安装Chrome浏览器
- 或设置代理: `export HTTP_PROXY=...`

## 技术栈

- **GUI**: CustomTkinter
- **网页处理**: Requests + Selenium + BeautifulSoup
- **文档处理**: PyPDF2 + pdfplumber + python-docx
- **图片处理**: Pillow + GPT-4o Vision
- **API**: OpenAI (via OpenRouter)

## 许可证

MIT License

## 作者

开发于 2026
