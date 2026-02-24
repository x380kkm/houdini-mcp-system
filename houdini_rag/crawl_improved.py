"""改进的爬虫 - 带进度显示"""
from scraper import HoudiniDocScraper
import time
import json


class ProgressScraper(HoudiniDocScraper):
    """带进度显示的爬虫"""

    def scrape(self):
        """开始爬取 - 带进度"""
        to_visit = [self.base_url]
        last_save = time.time()

        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)
            new_links = self.scrape_page(url)
            to_visit.extend(new_links)

            # 每10页显示一次进度
            if len(self.docs) % 10 == 0 and len(self.docs) > 0:
                print(f"\n进度: {len(self.docs)}/{self.max_pages} 页, 待访问: {len(to_visit)} 个链接")

            # 每30秒保存一次
            if time.time() - last_save > 30:
                self._save_progress()
                last_save = time.time()

        # 最终保存
        self._save_progress()
        print(f"\n完成! 爬取了 {len(self.docs)} 个页面")
        return self.docs

    def _save_progress(self):
        """保存进度"""
        output_file = self.output_dir / 'houdini_docs.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)
        print(f"  [已保存 {len(self.docs)} 页到 {output_file}]")


if __name__ == "__main__":
    print("=" * 60)
    print("爬取 Houdini 文档 (改进版)")
    print("=" * 60)

    scraper = ProgressScraper(
        base_url="https://www.sidefx.com/docs/houdini/",
        output_dir="./data/raw",
        max_pages=200,
        delay=0.5
    )

    start = time.time()
    docs = scraper.scrape()
    elapsed = time.time() - start

    print(f"\n总耗时: {int(elapsed//60)}分{int(elapsed%60)}秒")
    print(f"平均速度: {elapsed/len(docs):.2f}秒/页")
    print(f"总字符数: {sum(len(d['content']) for d in docs):,}")
