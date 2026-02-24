"""从本地Houdini安装提取文档"""
import zipfile
import json
from pathlib import Path
from bs4 import BeautifulSoup
import os


def extract_local_docs(help_dir, output_dir):
    """从本地help目录提取文档"""
    help_path = Path(help_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 找到所有ZIP文件
    zip_files = list(help_path.glob("*.zip"))
    print(f"找到 {len(zip_files)} 个ZIP文件")

    all_docs = []
    total_html = 0

    for zip_file in zip_files:
        print(f"\n处理: {zip_file.name}")

        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                # 提取到临时目录
                temp_dir = output_path / zip_file.stem
                zf.extractall(temp_dir)

                # 查找所有HTML文件
                html_files = list(temp_dir.rglob("*.html"))
                print(f"  找到 {len(html_files)} 个HTML文件")
                total_html += len(html_files)

                # 解析HTML
                for html_file in html_files:
                    try:
                        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                            soup = BeautifulSoup(f.read(), 'html.parser')

                        # 提取标题
                        title = soup.find('title')
                        title_text = title.get_text() if title else html_file.stem

                        # 提取内容
                        for script in soup(["script", "style"]):
                            script.decompose()

                        content = soup.get_text(separator='\n', strip=True)
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        content = '\n'.join(lines)

                        if len(content) > 100:  # 过滤太短的页面
                            doc = {
                                'url': f'local://{zip_file.stem}/{html_file.relative_to(temp_dir)}',
                                'title': title_text,
                                'content': content,
                                'source': zip_file.name
                            }
                            all_docs.append(doc)

                    except Exception as e:
                        print(f"    错误处理 {html_file.name}: {e}")

        except Exception as e:
            print(f"  错误: {e}")

    # 保存结果
    output_file = output_path / 'houdini_local_docs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)

    print(f"\n" + "=" * 60)
    print(f"提取完成!")
    print(f"=" * 60)
    print(f"处理的ZIP文件: {len(zip_files)}")
    print(f"总HTML文件: {total_html}")
    print(f"有效文档: {len(all_docs)}")
    print(f"总字符数: {sum(len(d['content']) for d in all_docs):,}")
    print(f"保存到: {output_file}")

    return all_docs


if __name__ == "__main__":
    help_dir = r"E:\steam\steamapps\common\Houdini Indie\houdini\help"
    output_dir = "./data/local_docs"

    docs = extract_local_docs(help_dir, output_dir)
