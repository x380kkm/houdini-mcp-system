# hda-doc

自动为 Houdini Digital Asset (HDA) 生成完整的技术文档

## 功能

- 🔌 自动导入 HDA 到 Houdini
- 📦 创建节点实例
- 📊 读取完整节点信息（参数、类型等）
- 🤖 使用 RAG 查询相关官方文档
- 📸 自动截图（网络视图、参数面板）
- 📝 生成完整的 Markdown 文档报告

## 使用方法

```bash
/hda-doc <HDA文件路径>
```

## 示例

```bash
# Windows 路径
/hda-doc "E:\dropbox\素材\GameJamStarterKit-UnrealEngine5\otls\HE_pipe.hda"

# 相对路径
/hda-doc "./my_assets/custom_tool.hda"
```

## 输出

生成的文档包含：

1. **基本信息**
   - HDA 文件路径
   - 节点类型和名称
   - 创建时间

2. **节点说明**（来自 RAG）
   - 节点功能描述
   - 使用场景
   - 相关文档链接

3. **参数列表**
   - 完整参数清单
   - 参数类型和默认值

4. **参数说明**（来自 RAG）
   - 主要参数的详细解释
   - 使用建议

5. **可视化**
   - 节点网络截图
   - 参数面板截图

6. **参考文档**
   - 相关官方文档链接
   - RAG 检索来源

## 输出位置

```
./hda_docs/
├── <asset_name>_<timestamp>/
│   ├── README.md              # 完整文档
│   ├── node_info.json         # 原始节点数据
│   ├── network_view.png       # 网络视图截图
│   └── parameters_view.png    # 参数面板截图
```

## 依赖

- Houdini MCP 服务器已启动
- Houdini RAG 系统已初始化
- 向量数据库已构建

## 技术细节

- 使用 MCP 远程控制 Houdini
- 通过 RAG 检索官方文档
- 自动处理 SOP/OBJ 等不同类型节点
- 生成结构化的 Markdown 报告

## 注意事项

- 确保 Houdini 已启动并运行 MCP 服务器
- HDA 文件路径必须存在
- 生成过程需要 20-30 秒
