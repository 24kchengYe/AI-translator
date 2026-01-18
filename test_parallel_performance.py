"""
并行翻译性能测试脚本
对比串行翻译和并行翻译的速度差异
"""
import time
from translation_engine import translation_engine


def test_translation_performance():
    """测试翻译性能"""

    # 准备测试数据（模拟网页中的多个文本节点）
    test_texts = [
        "Hello, welcome to our website!",
        "This is a comprehensive guide to web development.",
        "We offer various services including design and programming.",
        "Our team consists of experienced professionals.",
        "Contact us for more information about our products.",
        "Machine learning is revolutionizing the tech industry.",
        "Artificial intelligence can help automate many tasks.",
        "Data science combines statistics and programming.",
        "Cloud computing provides scalable infrastructure.",
        "Cybersecurity is essential for protecting digital assets.",
        "Mobile apps are increasingly popular among users.",
        "User experience design focuses on customer satisfaction.",
        "Responsive web design adapts to different screen sizes.",
        "API integration enables different systems to communicate.",
        "Database optimization improves application performance.",
        "Version control systems help manage code changes.",
        "Continuous integration automates the build process.",
        "Agile methodology emphasizes iterative development.",
        "Code review ensures quality and maintainability.",
        "Testing frameworks help catch bugs early.",
        "Documentation is crucial for project success.",
        "Open source software promotes collaboration.",
        "Microservices architecture improves scalability.",
        "Containerization simplifies deployment processes.",
        "Load balancing distributes traffic efficiently.",
        "Caching strategies reduce server load.",
        "CDN usage improves content delivery speed.",
        "SEO optimization increases website visibility.",
        "Analytics tools provide valuable insights.",
        "Performance monitoring identifies bottlenecks.",
        "Security audits protect against vulnerabilities.",
        "Backup systems prevent data loss.",
        "Disaster recovery plans ensure business continuity.",
        "Scalability planning prepares for growth.",
        "DevOps practices streamline operations.",
        "Infrastructure as code enables automation.",
        "Monitoring alerts notify of issues.",
        "Log aggregation aids in debugging.",
        "Error tracking helps fix problems quickly.",
        "User feedback guides product improvements.",
        "A/B testing validates design decisions.",
        "Feature flags enable controlled rollouts.",
        "Progressive web apps combine web and mobile benefits.",
        "GraphQL provides flexible API queries.",
        "WebSockets enable real-time communication.",
        "Service workers enable offline functionality.",
        "Lazy loading improves initial page load.",
        "Image optimization reduces bandwidth usage.",
        "Minification decreases file sizes.",
        "Compression algorithms save storage space."
    ]

    print("=" * 60)
    print("并行翻译性能测试")
    print("=" * 60)
    print(f"\n测试数据: {len(test_texts)} 个英文句子")
    print(f"目标语言: 中文")
    print("\n" + "=" * 60)

    # 测试1: 串行翻译
    print("\n[测试1] 串行翻译模式")
    print("-" * 60)
    start_time = time.time()

    try:
        serial_results = translation_engine.translate_batch(
            test_texts,
            source_lang="English",
            target_lang="Chinese",
            parallel=False  # 禁用并行
        )
        serial_time = time.time() - start_time

        print(f"✓ 串行翻译完成")
        print(f"  耗时: {serial_time:.2f} 秒")
        print(f"  平均每个文本: {serial_time/len(test_texts):.2f} 秒")
        print(f"  成功翻译: {len(serial_results)}/{len(test_texts)}")

        # 显示前3个翻译结果
        print(f"\n  示例翻译结果:")
        for i in range(min(3, len(serial_results))):
            print(f"    原文: {test_texts[i]}")
            print(f"    译文: {serial_results[i]}")
            print()

    except Exception as e:
        print(f"✗ 串行翻译失败: {str(e)}")
        serial_time = None
        serial_results = None

    # 测试2: 并行翻译
    print("\n" + "=" * 60)
    print("\n[测试2] 并行翻译模式")
    print("-" * 60)
    start_time = time.time()

    try:
        parallel_results = translation_engine.translate_batch(
            test_texts,
            source_lang="English",
            target_lang="Chinese",
            parallel=True  # 启用并行
        )
        parallel_time = time.time() - start_time

        print(f"✓ 并行翻译完成")
        print(f"  耗时: {parallel_time:.2f} 秒")
        print(f"  平均每个文本: {parallel_time/len(test_texts):.2f} 秒")
        print(f"  成功翻译: {len(parallel_results)}/{len(test_texts)}")
        print(f"  并发线程数: {translation_engine.max_workers}")

        # 显示前3个翻译结果
        print(f"\n  示例翻译结果:")
        for i in range(min(3, len(parallel_results))):
            print(f"    原文: {test_texts[i]}")
            print(f"    译文: {parallel_results[i]}")
            print()

    except Exception as e:
        print(f"✗ 并行翻译失败: {str(e)}")
        parallel_time = None
        parallel_results = None

    # 性能对比
    print("\n" + "=" * 60)
    print("\n[性能对比]")
    print("-" * 60)

    if serial_time and parallel_time:
        speedup = serial_time / parallel_time
        time_saved = serial_time - parallel_time
        efficiency = (speedup / translation_engine.max_workers) * 100

        print(f"串行模式耗时:   {serial_time:.2f} 秒")
        print(f"并行模式耗时:   {parallel_time:.2f} 秒")
        print(f"")
        print(f"⚡ 速度提升:     {speedup:.2f}x")
        print(f"⏱️  节省时间:     {time_saved:.2f} 秒 ({time_saved/serial_time*100:.1f}%)")
        print(f"📊 并行效率:     {efficiency:.1f}%")
        print(f"")

        if speedup >= 2.0:
            print("🎉 性能提升显著！并行翻译效果很好。")
        elif speedup >= 1.5:
            print("👍 性能有明显提升，并行翻译有效。")
        elif speedup >= 1.2:
            print("✓ 性能略有提升，可以考虑调整并发数。")
        else:
            print("⚠️  性能提升不明显，可能需要检查网络或API限制。")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_translation_performance()
