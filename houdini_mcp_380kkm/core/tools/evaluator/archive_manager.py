"""
归档管理工具
管理评估历史的项目-节点归档系统
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid
import argparse


class ArchiveManager:
    """归档管理器"""

    def __init__(self, base_dir: str = "./archives"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_node_folder_name(self, node_path: str, node_uuid: str) -> str:
        """
        生成节点文件夹名称
        格式: 节点名_序号
        """
        # 从路径提取节点名
        node_name = node_path.split('/')[-1]

        # 查找现有序号
        project_dirs = list(self.base_dir.glob("*/"))
        max_seq = 0

        for proj_dir in project_dirs:
            for node_dir in proj_dir.glob(f"{node_name}_*"):
                try:
                    seq = int(node_dir.name.split('_')[-1])
                    max_seq = max(max_seq, seq)
                except ValueError:
                    continue

        return f"{node_name}_{max_seq + 1:03d}"

    def _load_or_create_metadata(self, node_dir: Path, node_path: str, node_uuid: str) -> Dict:
        """加载或创建节点元数据"""
        metadata_file = node_dir / "metadata.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        metadata = {
            "node_path": node_path,
            "node_uuid": node_uuid,
            "created_at": datetime.now().isoformat(),
            "folder_name": node_dir.name,
            "evaluation_count": 0
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata

    def create_project(self, project_name: str) -> Path:
        """创建新项目"""
        # 查找现有项目序号
        existing = list(self.base_dir.glob(f"project_{project_name}_*"))
        max_seq = 0

        for proj in existing:
            try:
                seq = int(proj.name.split('_')[-1])
                max_seq = max(max_seq, seq)
            except ValueError:
                continue

        project_dir = self.base_dir / f"project_{project_name}_{max_seq + 1:03d}"
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ 创建项目: {project_dir}")
        return project_dir

    def add_evaluation(
        self,
        project_name: str,
        node_path: str,
        image_path: str,
        evaluation_result: Dict[str, Any],
        parameters: Dict[str, Any],
        node_uuid: Optional[str] = None
    ) -> Path:
        """
        添加评估记录到归档

        Args:
            project_name: 项目名称
            node_path: 节点路径 (如 /obj/mountain_terrain/base_mountains)
            image_path: 渲染图片路径
            evaluation_result: 评估结果
            parameters: 参数设置
            node_uuid: 节点 UUID (可选，自动生成)
        """
        # 查找项目目录
        project_dirs = list(self.base_dir.glob(f"project_{project_name}_*"))
        if not project_dirs:
            print(f"⚠️  项目不存在，自动创建...")
            project_dir = self.create_project(project_name)
        else:
            project_dir = sorted(project_dirs)[-1]  # 使用最新的

        # 生成或使用 UUID
        if node_uuid is None:
            node_uuid = str(uuid.uuid4())

        # 查找或创建节点目录
        node_name = node_path.split('/')[-1]
        node_dirs = list(project_dir.glob(f"{node_name}_*"))

        if node_dirs:
            # 检查是否是同一个节点 (通过 UUID)
            for node_dir in node_dirs:
                metadata = self._load_or_create_metadata(node_dir, node_path, node_uuid)
                if metadata.get('node_uuid') == node_uuid:
                    break
            else:
                # 新节点
                folder_name = self._get_node_folder_name(node_path, node_uuid)
                node_dir = project_dir / folder_name
                node_dir.mkdir(parents=True, exist_ok=True)
                metadata = self._load_or_create_metadata(node_dir, node_path, node_uuid)
        else:
            # 第一个节点
            folder_name = f"{node_name}_001"
            node_dir = project_dir / folder_name
            node_dir.mkdir(parents=True, exist_ok=True)
            metadata = self._load_or_create_metadata(node_dir, node_path, node_uuid)

        # 创建评估记录目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        eval_dir = node_dir / timestamp
        eval_dir.mkdir(parents=True, exist_ok=True)

        # 复制图片
        image_src = Path(image_path)
        if image_src.exists():
            shutil.copy2(image_src, eval_dir / "render.png")

        # 保存评估结果
        with open(eval_dir / "evaluation.json", 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, indent=2, ensure_ascii=False)

        # 保存参数
        with open(eval_dir / "parameters.json", 'w', encoding='utf-8') as f:
            json.dump(parameters, f, indent=2, ensure_ascii=False)

        # 更新元数据
        metadata['evaluation_count'] += 1
        metadata['last_evaluation'] = timestamp
        with open(node_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"✅ 添加评估记录: {eval_dir}")
        return eval_dir

    def cleanup_old_records(self, days: int = 30, interactive: bool = True):
        """
        清理旧记录

        Args:
            days: 保留天数
            interactive: 是否交互式确认
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        to_delete = []

        # 扫描所有评估记录
        for project_dir in self.base_dir.glob("project_*"):
            for node_dir in project_dir.glob("*_[0-9][0-9][0-9]"):
                for eval_dir in node_dir.glob("*"):
                    if not eval_dir.is_dir():
                        continue

                    try:
                        eval_time = datetime.strptime(eval_dir.name, '%Y%m%d_%H%M%S')
                        if eval_time < cutoff_date:
                            to_delete.append(eval_dir)
                    except ValueError:
                        continue

        if not to_delete:
            print(f"✅ 没有超过 {days} 天的记录")
            return

        print(f"\n发现 {len(to_delete)} 条超过 {days} 天的记录:")
        for i, path in enumerate(to_delete[:10], 1):
            print(f"  {i}. {path.relative_to(self.base_dir)}")

        if len(to_delete) > 10:
            print(f"  ... 还有 {len(to_delete) - 10} 条")

        if interactive:
            response = input(f"\n是否删除这些记录? (y/N): ")
            if response.lower() != 'y':
                print("❌ 取消删除")
                return

        # 执行删除
        deleted = 0
        for path in to_delete:
            try:
                shutil.rmtree(path)
                deleted += 1
            except Exception as e:
                print(f"⚠️  删除失败 {path}: {e}")

        print(f"✅ 已删除 {deleted} 条记录")

    def list_projects(self):
        """列出所有项目"""
        projects = list(self.base_dir.glob("project_*"))

        if not projects:
            print("没有项目")
            return

        print(f"\n项目列表 ({len(projects)} 个):")
        for proj in sorted(projects):
            nodes = list(proj.glob("*_[0-9][0-9][0-9]"))
            print(f"  📁 {proj.name} ({len(nodes)} 个节点)")

    def list_nodes(self, project_name: str):
        """列出项目中的所有节点"""
        project_dirs = list(self.base_dir.glob(f"project_{project_name}_*"))

        if not project_dirs:
            print(f"❌ 项目不存在: {project_name}")
            return

        project_dir = sorted(project_dirs)[-1]
        nodes = list(project_dir.glob("*_[0-9][0-9][0-9]"))

        if not nodes:
            print(f"项目 {project_dir.name} 没有节点")
            return

        print(f"\n节点列表 ({len(nodes)} 个):")
        for node_dir in sorted(nodes):
            metadata_file = node_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                eval_count = metadata.get('evaluation_count', 0)
                node_path = metadata.get('node_path', 'N/A')
                print(f"  🔷 {node_dir.name}")
                print(f"     路径: {node_path}")
                print(f"     评估: {eval_count} 次")


def main():
    parser = argparse.ArgumentParser(description='归档管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # create-project
    create_parser = subparsers.add_parser('create-project', help='创建新项目')
    create_parser.add_argument('name', help='项目名称')

    # add-evaluation
    add_parser = subparsers.add_parser('add-evaluation', help='添加评估记录')
    add_parser.add_argument('--project', required=True, help='项目名称')
    add_parser.add_argument('--node', required=True, help='节点路径')
    add_parser.add_argument('--image', required=True, help='图片路径')
    add_parser.add_argument('--result', help='评估结果 JSON 文件')
    add_parser.add_argument('--params', help='参数 JSON 文件')

    # cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧记录')
    cleanup_parser.add_argument('--days', type=int, default=30, help='保留天数')
    cleanup_parser.add_argument('--yes', action='store_true', help='跳过确认')

    # list-projects
    subparsers.add_parser('list-projects', help='列出所有项目')

    # list-nodes
    list_parser = subparsers.add_parser('list-nodes', help='列出项目节点')
    list_parser.add_argument('project', help='项目名称')

    args = parser.parse_args()
    manager = ArchiveManager()

    if args.command == 'create-project':
        manager.create_project(args.name)

    elif args.command == 'add-evaluation':
        # 加载结果和参数
        result = {}
        if args.result and Path(args.result).exists():
            with open(args.result, 'r', encoding='utf-8') as f:
                result = json.load(f)

        params = {}
        if args.params and Path(args.params).exists():
            with open(args.params, 'r', encoding='utf-8') as f:
                params = json.load(f)

        manager.add_evaluation(
            args.project,
            args.node,
            args.image,
            result,
            params
        )

    elif args.command == 'cleanup':
        manager.cleanup_old_records(args.days, not args.yes)

    elif args.command == 'list-projects':
        manager.list_projects()

    elif args.command == 'list-nodes':
        manager.list_nodes(args.project)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
