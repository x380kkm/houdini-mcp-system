"""
Prompt 管理器
从 prompts.yaml 加载和管理不同阶段的评估 Prompt
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class PromptManager:
    """Prompt 模板管理器"""

    def __init__(self, prompts_file: str = "prompts.yaml"):
        """初始化 Prompt 管理器"""
        self.prompts_file = Path(__file__).parent / prompts_file
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """加载 Prompt 配置"""
        if not self.prompts_file.exists():
            raise FileNotFoundError(f"Prompts 配置文件不存在: {self.prompts_file}")

        with open(self.prompts_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('prompts', {})

    def get_stages(self) -> list:
        """获取所有可用的阶段"""
        return list(self.prompts.keys())

    def get_prompt(self, stage: str, parameters: Dict[str, Any]) -> str:
        """
        获取指定阶段的 Prompt

        Args:
            stage: 阶段名称（如 'main_mountain', 'mid_detail'）
            parameters: 参数字典，用于替换模板中的占位符

        Returns:
            格式化后的 Prompt 字符串
        """
        if stage not in self.prompts:
            raise ValueError(f"未知的阶段: {stage}。可用阶段: {self.get_stages()}")

        prompt_config = self.prompts[stage]
        template = prompt_config.get('template', '')

        # 替换参数
        try:
            formatted_prompt = template.format(**parameters)
            return formatted_prompt
        except KeyError as e:
            raise ValueError(f"缺少必需的参数: {e}")

    def get_task_name(self, stage: str) -> str:
        """获取阶段的任务名称"""
        if stage not in self.prompts:
            raise ValueError(f"未知的阶段: {stage}")
        return self.prompts[stage].get('task_name', stage)

    def get_description(self, stage: str) -> str:
        """获取阶段的描述"""
        if stage not in self.prompts:
            raise ValueError(f"未知的阶段: {stage}")
        return self.prompts[stage].get('description', '')

    def validate_parameters(self, stage: str, parameters: Dict[str, Any]) -> tuple:
        """
        验证参数是否完整

        Returns:
            (is_valid, missing_params)
        """
        if stage not in self.prompts:
            return False, [f"未知的阶段: {stage}"]

        template = self.prompts[stage].get('template', '')

        # 提取模板中的所有占位符
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)

        # 检查缺失的参数
        missing = [p for p in placeholders if p not in parameters]

        return len(missing) == 0, missing


# 便捷函数
def get_prompt_for_stage(stage: str, parameters: Dict[str, Any]) -> str:
    """
    便捷函数：获取指定阶段的 Prompt

    Args:
        stage: 阶段名称
        parameters: 参数字典

    Returns:
        格式化后的 Prompt
    """
    manager = PromptManager()
    return manager.get_prompt(stage, parameters)


def list_available_stages() -> list:
    """列出所有可用的阶段"""
    manager = PromptManager()
    return manager.get_stages()


if __name__ == '__main__':
    # 测试
    manager = PromptManager()

    print("可用阶段:")
    for stage in manager.get_stages():
        print(f"  - {stage}: {manager.get_description(stage)}")

    # 测试主山脉阶段
    print("\n测试主山脉 Prompt:")
    params = {
        'terrain_size_x': 1000,
        'terrain_size_y': 1000,
        'grid_resolution_x': 512,
        'grid_resolution_y': 512,
        'amplitude': 500,
        'element_size': 100,
        'roughness': 0.7,
        'octaves': 12,
        'lacunarity': 2.5
    }

    is_valid, missing = manager.validate_parameters('main_mountain', params)
    if is_valid:
        prompt = manager.get_prompt('main_mountain', params)
        print(prompt[:500] + "...")
    else:
        print(f"缺少参数: {missing}")
