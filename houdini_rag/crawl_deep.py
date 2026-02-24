"""深度爬取 - 从已有页面的子页面开始"""
from scraper import HoudiniDocScraper
import json
import time
from pathlib import Path


class DeepScraper(HoudiniDocScraper):
    """深度爬取器 - 从种子页面开始"""

    def scrape_from_seeds(self, seed_file):
        """从种子文件开始爬取"""
        # 加载已有页面作为种子
        with open(seed_file, 'r', encoding='utf-8') as f:
            seeds = json.load(f)

        print(f"加载了 {len(seeds)} 个种子页面")

        # 标记种子页面为已访问
        for seed in seeds:
            self.visited.add(seed['url'])
            self.docs.append(seed)

        # 从种子页面提取所有链接
        to_visit = []
        for seed in seeds:
            print(f"\n从种子页面提取链接: {seed['title'][:50]}")
            links = self._extract_links_from_url(seed['url'])
            print(f"  找到 {len(links)} 个新链接")
            to_visit.extend(links)

        # 去重
        to_visit = list(set(to_visit))
        print(f"\n总共 {len(to_visit)} 个待访问链接")
        print("开始爬取...\n")

        # 开始爬取
        count = 0
        last_save = time.time()

        while to_visit and len(self.docs) < self.max_pages:
            url = to_visit.pop(0)
            if url in self.visited:
                continue

            new_links = self.scrape_page(url)
            to_visit.extend(new_links)
            count += 1

            # 每10页显示进度
            if count % 10 == 0:
                print(f"进度: {len(self.docs)}/{self.max_pages} 页, 待访问: {len(to_visit)}")

            # 每30秒保存一次
            if time.time() - last_save > 30:
                self._save()
                last_save = time.time()

        # 最终保存
        self._save()
        return self.docs

    def _extract_links_from_url(self, url):
        """从URL提取链接"""
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin

            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].split('#')[0]
                if not href:
                    continue

                full_url = urljoin(url, href)
                full_url = full_url.rstrip('/')

                if (self.is_valid_url(full_url) and
                    full_url not in self.visited):
                    links.append(full_url)

            return list(set(links))
        except Exception as e:
            print(f"  错误: {e}")
            return []

    def _save(self):
        """保存进度"""
        output_file = self.output_dir / 'houdini_docs.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)
        print(f"  [已保存 {len(self.docs)} 页]")


if __name__ == "__main__":
    print("=" * 60)
    print("深度爬取 Houdini 文档")
    print("=" * 60)

    scraper = DeepScraper(
        base_url="https://www.sidefx.com/docs/houdini/",
        output_dir="./data/raw",
        max_pages=200,
        delay=0.5
    )

    start = time.time()
    docs = scraper.scrape_from_seeds('./data/raw/houdini_docs.json')
    elapsed = time.time() - start

    print("\n" + "=" * 60)
    print("爬取完成!")
    print("=" * 60)
    print(f"总页面数: {len(docs)}")
    print(f"耗时: {int(elapsed//60)}分{int(elapsed%60)}秒")
    print(f"平均速度: {elapsed/len(docs):.2f}秒/页")
    print(f"总字符数: {sum(len(d['content']) for d in docs):,}")
