"""从本地Houdini TXT文档提取内容"""
import json
from pathlib import Path


def extract_txt_docs(base_dir, output_file):
    """提取所有TXT文档"""
    base_path = Path(base_dir)
    all_docs = []

    # 遍历所有子目录
    for category_dir in base_path.iterdir():
        if not category_dir.is_dir():
            continue

        category = category_dir.name
        print(f"\n处理分类: {category}")

        # 查找所有TXT文件
        txt_files = list(category_dir.rglob("*.txt"))
        print(f"  找到 {len(txt_files)} 个TXT文件")

        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 过滤太短的文件
                if len(content) > 100:
                    # 从文件名生成标题
                    title = txt_file.stem.replace('_', ' ').title()

                    doc = {
                        'url': f'local://{category}/{txt_file.relative_to(category_dir)}',
                        'title': f'{category.title()}: {title}',
                        'content': content,
                        'category': category,
                        'file': txt_file.name
                    }
                    all_docs.append(doc)

            except Exception as e:
                print(f"    错误: {txt_file.name} - {e}")

    # 保存结果
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)

    # 统计
    print("\n" + "=" * 60)
    print("提取完成!")
    print("=" * 60)
    print(f"总文档数: {len(all_docs)}")
    print(f"总字符数: {sum(len(d['content']) for d in all_docs):,}")
    print(f"平均文档大小: {sum(len(d['content']) for d in all_docs) // len(all_docs):,} 字符")

    # 按分类统计
    categories = {}
    for doc in all_docs:
        cat = doc['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {cat}: {count} 个文档")

    print(f"\n保存到: {output_path}")
    return all_docs


if __name__ == "__main__":
    base_dir = "./data/local_docs"
    output_file = "./data/raw/houdini_docs.json"

    docs = extract_txt_docs(base_dir, output_file)
