"""完整文档爬取"""
from scraper import HoudiniDocScraper
import yaml
import time


def crawl_full_docs():
    """爬取完整文档"""
    print("=" * 60)
    print("Houdini 完整文档爬取")
    print("=" * 60)

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    max_pages = config['scraper']['max_pages']
    print(f"\n目标: {config['scraper']['base_url']}")
    print(f"最大页面数: {max_pages}")
    print(f"延迟: {config['scraper']['delay']}秒")
    print("\n开始爬取...\n")

    start_time = time.time()

    scraper = HoudiniDocScraper(
        base_url=config['scraper']['base_url'],
        output_dir=config['scraper']['output_dir'],
        max_pages=max_pages,
        delay=config['scraper']['delay']
    )

    docs = scraper.scrape()

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print("\n" + "=" * 60)
    print(f"✓ 爬取完成!")
    print("=" * 60)
    print(f"总页面数: {len(docs)}")
    print(f"耗时: {minutes}分{seconds}秒")
    print(f"平均速度: {elapsed/len(docs):.2f}秒/页")
    print(f"数据文件: data/raw/houdini_docs.json")

    # 统计信息
    total_chars = sum(len(doc['content']) for doc in docs)
    print(f"\n内容统计:")
    print(f"  总字符数: {total_chars:,}")
    print(f"  平均页面大小: {total_chars//len(docs):,} 字符")

    # 显示前10个和最后10个文档
    print(f"\n前10个文档:")
    for i, doc in enumerate(docs[:10], 1):
        print(f"  {i}. {doc['title'][:60]}")

    if len(docs) > 20:
        print(f"\n最后10个文档:")
        for i, doc in enumerate(docs[-10:], len(docs)-9):
            print(f"  {i}. {doc['title'][:60]}")

    return docs


if __name__ == "__main__":
    crawl_full_docs()
