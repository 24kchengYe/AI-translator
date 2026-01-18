"""
UI测试脚本 - 验证字体和界面
"""
import sys

def test_ui():
    """测试UI启动和字体"""
    print("=" * 60)
    print("UI测试")
    print("=" * 60)

    try:
        print("\n1. 导入ttkbootstrap...")
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import *
        print("   ✓ ttkbootstrap导入成功")

        print("\n2. 创建测试窗口...")
        root = ttk.Window(themename="flatly")
        root.title("字体测试")
        root.geometry("400x300")
        print("   ✓ 窗口创建成功")

        print("\n3. 设置字体...")
        from tkinter import font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial", size=10)
        print("   ✓ 字体设置成功")

        print("\n4. 创建测试组件...")

        # 标签
        label = ttk.Label(
            root,
            text="这是Arial字体测试 - This is Arial font test",
            font=("Arial", 12)
        )
        label.pack(pady=20)

        # 按钮
        btn = ttk.Button(
            root,
            text="测试按钮 Test Button",
            bootstyle="primary"
        )
        btn.pack(pady=10)

        # Labelframe
        frame = ttk.Labelframe(
            root,
            text="测试框架 Test Frame",
            bootstyle="info"
        )
        frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)

        inner_label = ttk.Label(
            frame,
            text="内部标签 Inner Label",
            font=("Arial", 10)
        )
        inner_label.pack(pady=20)

        print("   ✓ 组件创建成功")

        print("\n" + "=" * 60)
        print("✓ UI测试通过！")
        print("=" * 60)
        print("\n请检查窗口中的字体是否都是Arial")
        print("按Ctrl+C或关闭窗口退出")
        print("=" * 60)

        root.mainloop()

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_ui()
