"""命令行界面"""
import yaml
import argparse
from pathlib import Path
from scraper import HoudiniDocScraper
from indexer import DocumentIndexer
from rag_engine import HoudiniRAG


def load_config(config_path='config.yaml'):
    """加载配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def cmd_scrape(args):
    """爬取文档"""
    config = load_config(args.config)
    scraper = HoudiniDocScraper(
        base_url=config['scraper']['base_url'],
        output_dir=config['scraper']['output_dir'],
        max_pages=args.max_pages or config['scraper']['max_pages'],
        delay=config['scraper']['delay']
    )
    scraper.scrape()


def cmd_index(args):
    """构建索引"""
    config = load_config(args.config)
    indexer = DocumentIndexer(config)

    json_file = Path(config['scraper']['output_dir']) / 'houdini_docs.json'
    if not json_file.exists():
        print(f"错误: 找不到文档文件 {json_file}")
        print("请先运行: python cli.py scrape")
        return

    docs = indexer.load_documents(json_file)
    indexer.build_index(docs)


def cmd_query(args):
    """查询"""
    config = load_config(args.config)
    rag = HoudiniRAG(config)

    if args.interactive:
        print("Houdini RAG 交互模式 (输入 'quit' 退出)\n")
        while True:
            question = input("问题: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break

            if not question:
                continue

            print("\n查询中...")
            result = rag.query(question)

            print(f"\n回答:\n{result['answer']}\n")
            print("相关文档:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']}")
                print(f"   {source['url']}\n")
    else:
        result = rag.query(args.question)
        print(f"回答:\n{result['answer']}\n")
        print("相关文档:")
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['title']}")
            print(f"   {source['url']}")


def cmd_search(args):
    """相似度搜索"""
    config = load_config(args.config)
    rag = HoudiniRAG(config)

    results = rag.search_similar(args.query, k=args.top_k)
    print(f"找到 {len(results)} 个相关文档:\n")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['title']}")
        print(f"   {doc['url']}")
        print(f"   {doc['content']}\n")


def main():
    parser = argparse.ArgumentParser(description='Houdini RAG 系统')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # scrape 命令
    scrape_parser = subparsers.add_parser('scrape', help='爬取Houdini文档')
    scrape_parser.add_argument('--max-pages', type=int, help='最大爬取页面数')

    # index 命令
    index_parser = subparsers.add_parser('index', help='构建向量索引')

    # query 命令
    query_parser = subparsers.add_parser('query', help='查询')
    query_parser.add_argument('question', nargs='?', help='问题')
    query_parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')

    # search 命令
    search_parser = subparsers.add_parser('search', help='相似度搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--top-k', type=int, default=5, help='返回结果数')

    args = parser.parse_args()

    if args.command == 'scrape':
        cmd_scrape(args)
    elif args.command == 'index':
        cmd_index(args)
    elif args.command == 'query':
        cmd_query(args)
    elif args.command == 'search':
        cmd_search(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
