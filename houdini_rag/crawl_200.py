"""爬取更多页面 - 200页"""
from scraper import HoudiniDocScraper
import time


def crawl_200_pages():
    """爬取200个页面"""
    print("=" * 60)
    print("爬取 200 个 Houdini 文档页面")
    print("=" * 60)

    start_time = time.time()

    scraper = HoudiniDocScraper(
        base_url="https://www.sidefx.com/docs/houdini/",
        output_dir="./data/raw",
        max_pages=200,
        delay=0.8  # 稍微快一点
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

    # 统计
    total_chars = sum(len(doc['content']) for doc in docs)
    print(f"\n内容统计:")
    print(f"  总字符数: {total_chars:,}")
    print(f"  平均页面: {total_chars//len(docs):,} 字符")
    print(f"  数据文件: data/raw/houdini_docs.json")

    return docs


if __name__ == "__main__":
    crawl_200_pages()
