"""Houdini 文档爬虫"""
import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json


class HoudiniDocScraper:
    def __init__(self, base_url, output_dir, max_pages=100, delay=1.0):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.docs = []

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_valid_url(self, url):
        """检查URL是否有效"""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)

        # 必须是同一域名
        if parsed.netloc != base_parsed.netloc:
            return False

        # 移除URL片段和查询参数进行比较
        clean_url = url.split('#')[0].split('?')[0]

        # 排除非文档页面
        exclude_patterns = ['.pdf', '.zip', '.tar', '.gz', 'download', 'forum']
        if any(pattern in clean_url.lower() for pattern in exclude_patterns):
            return False

        return True

    def extract_content(self, soup):
        """提取页面主要内容"""
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()

        # 尝试找到主要内容区域
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')

        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)

        # 清理多余空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def scrape_page(self, url):
        """爬取单个页面"""
        if url in self.visited or len(self.visited) >= self.max_pages:
            return []

        try:
            print(f"爬取: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            self.visited.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取内容
            title = soup.find('title')
            title_text = title.get_text() if title else url
            content = self.extract_content(soup)

            doc = {
                'url': url,
                'title': title_text,
                'content': content
            }
            self.docs.append(doc)

            # 查找链接
            links = []
            seen_in_page = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                # 移除片段标识符
                href = href.split('#')[0]
                if not href:
                    continue

                full_url = urljoin(url, href)
                # 标准化URL
                full_url = full_url.rstrip('/')

                if (self.is_valid_url(full_url) and
                    full_url not in self.visited and
                    full_url not in seen_in_page):
                    links.append(full_url)
                    seen_in_page.add(full_url)

            time.sleep(self.delay)
            return links

        except Exception as e:
            print(f"错误 {url}: {e}")
            return []

    def scrape(self):
        """开始爬取"""
        to_visit = [self.base_url]

        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)
            new_links = self.scrape_page(url)
            to_visit.extend(new_links)

        # 保存结果
        output_file = self.output_dir / 'houdini_docs.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)

        print(f"\n完成! 爬取了 {len(self.docs)} 个页面")
        print(f"保存到: {output_file}")

        return self.docs


if __name__ == "__main__":
    scraper = HoudiniDocScraper(
        base_url="https://www.sidefx.com/docs/houdini/",
        output_dir="./data/raw",
        max_pages=50,
        delay=1.0
    )
    scraper.scrape()
