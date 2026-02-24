"""
图片评估代理工具
使用 OpenAI API 兼容接口来评估 Houdini 生成的地形截图
"""

import os
import sys
import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
import requests
from PIL import Image
import io

from .prompt_manager import PromptManager


class ImageEvaluator:
    """图片评估器"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化评估器"""
        self.config = self._load_config(config_path)
        self.prompt_manager = PromptManager()
        self._setup_logging()
        self._ensure_dirs()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))

        handlers = []
        if log_config.get('console', True):
            handlers.append(logging.StreamHandler())

        log_file = log_config.get('log_file')
        if log_file:
            log_path = Path(__file__).parent / log_file
            handlers.append(logging.FileHandler(log_path, encoding='utf-8'))

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger('ImageEvaluator')

    def _ensure_dirs(self):
        """确保必要的目录存在"""
        eval_config = self.config.get('evaluation', {})
        if eval_config.get('save_history', True):
            history_dir = Path(__file__).parent / eval_config.get('history_dir', './evaluation_history')
            history_dir.mkdir(parents=True, exist_ok=True)

    def _resize_image(self, image_path: str) -> Image.Image:
        """调整图片大小"""
        img = Image.open(image_path)
        img_config = self.config.get('image', {})

        if img_config.get('auto_resize', True):
            max_size = img_config.get('max_size', 2048)
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                self.logger.info(f"图片已调整大小: {img.size}")

        return img

    def _image_to_base64(self, img: Image.Image) -> str:
        """将图片转换为 base64"""
        buffer = io.BytesIO()
        quality = self.config.get('image', {}).get('quality', 85)
        img.save(buffer, format='PNG', quality=quality)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def evaluate(self, image_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估图片（使用 config.yaml 中的通用模板）

        Args:
            image_path: 图片路径
            parameters: 当前参数设置

        Returns:
            评估结果字典
        """
        self.logger.info(f"开始评估图片: {image_path}")

        # 检查文件
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 处理图片
        img = self._resize_image(image_path)
        img_base64 = self._image_to_base64(img)

        # 构建提示词
        eval_config = self.config.get('evaluation', {})
        prompt_template = eval_config.get('prompt_template', '')
        param_str = '\n'.join([f"- {k}: {v}" for k, v in parameters.items()])
        prompt = prompt_template.format(parameters=param_str)

        # 调用 API
        result = self._call_api(prompt, img_base64)

        # 保存历史
        if eval_config.get('save_history', True):
            self._save_history(image_path, parameters, result)

        return result

    def evaluate_stage(self, image_path: str, stage: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估指定阶段的图片（使用 prompts.yaml 中的专用模板）

        Args:
            image_path: 图片路径
            stage: 阶段名称（如 'main_mountain', 'mid_detail'）
            parameters: 节点参数字典

        Returns:
            评估结果字典
        """
        self.logger.info(f"开始评估图片 [{stage}]: {image_path}")

        # 检查文件
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 验证参数
        is_valid, missing = self.prompt_manager.validate_parameters(stage, parameters)
        if not is_valid:
            raise ValueError(f"缺少必需的参数: {missing}")

        # 处理图片
        img = self._resize_image(image_path)
        img_base64 = self._image_to_base64(img)

        # 获取阶段专用 Prompt
        prompt = self.prompt_manager.get_prompt(stage, parameters)

        # 调用 API
        result = self._call_api(prompt, img_base64)

        # 添加阶段信息
        result['stage'] = stage
        result['task_name'] = self.prompt_manager.get_task_name(stage)

        # 保存历史
        eval_config = self.config.get('evaluation', {})
        if eval_config.get('save_history', True):
            self._save_history(image_path, parameters, result, stage)

        return result

    def _call_api(self, prompt: str, image_base64: str) -> Dict[str, Any]:
        """调用 OpenAI 兼容 API"""
        api_config = self.config.get('api', {})
        base_url = api_config.get('base_url', '').rstrip('/')
        api_key = api_config.get('api_key', '')
        model = api_config.get('model', 'gpt-4-vision-preview')
        timeout = api_config.get('timeout', 60)
        max_retries = api_config.get('max_retries', 3)

        if not api_key or api_key == 'your-api-key-here':
            raise ValueError("请在 config.yaml 中配置有效的 API Key")

        url = f"{base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000  # 增加 token 限制，避免截断
        }

        # 重试逻辑
        for attempt in range(max_retries):
            try:
                self.logger.info(f"调用 API (尝试 {attempt + 1}/{max_retries})...")
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()

                data = response.json()
                content = data['choices'][0]['message']['content']

                # 清理 markdown 代码块标记
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]  # 移除 ```json
                if content.startswith('```'):
                    content = content[3:]  # 移除 ```
                if content.endswith('```'):
                    content = content[:-3]  # 移除结尾的 ```
                content = content.strip()

                # 检查是否被截断
                finish_reason = data['choices'][0].get('finish_reason')
                if finish_reason == 'length':
                    self.logger.warning("API 响应被截断，可能需要增加 max_tokens")

                self.logger.info("API 调用成功")
                return {
                    'success': True,
                    'evaluation': content,
                    'raw_response': data
                }

            except requests.exceptions.RequestException as e:
                self.logger.error(f"API 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': str(e)
                    }

    def _save_history(self, image_path: str, parameters: Dict[str, Any], result: Dict[str, Any], stage: str = None):
        """保存评估历史"""
        eval_config = self.config.get('evaluation', {})
        history_dir = Path(__file__).parent / eval_config.get('history_dir', './evaluation_history')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stage_suffix = f"_{stage}" if stage else ""
        history_file = history_dir / f"evaluation_{timestamp}{stage_suffix}.json"

        history_data = {
            'timestamp': timestamp,
            'image_path': image_path,
            'stage': stage,
            'parameters': parameters,
            'result': result
        }

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"评估历史已保存: {history_file}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='图片评估代理工具')
    parser.add_argument('image', help='图片路径')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--params', help='参数 JSON 字符串')

    args = parser.parse_args()

    # 解析参数
    parameters = {}
    if args.params:
        parameters = json.loads(args.params)

    # 创建评估器
    evaluator = ImageEvaluator(args.config)

    # 执行评估
    result = evaluator.evaluate(args.image, parameters)

    # 输出结果
    if result['success']:
        print("\n" + "=" * 60)
        print("评估结果")
        print("=" * 60)
        print(result['evaluation'])
        print("=" * 60)
    else:
        print(f"\n❌ 评估失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
