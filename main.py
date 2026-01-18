"""
AI翻译软件主程序
启动GUI应用
"""
import sys
from gui.main_window_new import run_gui


def main():
    """主函数"""
    try:
        print("启动AI翻译助手...")
        print("=" * 50)
        print("使用前请确保:")
        print("1. 已安装所有依赖: pip install -r requirements.txt")
        print("2. 已配置.env文件中的API密钥")
        print("=" * 50)

        # 运行GUI
        run_gui()

    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
