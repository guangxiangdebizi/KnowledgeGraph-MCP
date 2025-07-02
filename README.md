# 德国家族企业知识图谱 MCP 服务器

🏢 **KnowledgeGraph-MCP** - 专门为德国家族企业知识图谱构建的 Model Context Protocol (MCP) 服务器

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-orange.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目简介

本项目提供一个专业的 MCP 服务器，让 AI 助手（如 Claude、Cursor、Cline 等）能够直接访问和查询德国家族企业知识图谱数据库。通过 Neo4j 图数据库存储结构化知识，支持复杂的关系查询和语义搜索。

### 🎯 项目特色

- **垂直领域专业化**: 专注于德国家族企业领域知识
- **智能查询支持**: AI 可自然构造 Cypher 查询语句
- **结构化知识图谱**: 层次化组织的企业管理、创新、传承知识
- **即插即用**: 快速集成到现有 AI 工作流程
- **安全可靠**: 只读访问，防止数据意外修改

## ✨ 功能特性

### 🔍 核心工具

1. **`explain_database_structure`** - 数据库结构解释器
   - 完整的知识图谱结构概览
   - 节点类型、关系类型详细说明
   - 实际数据样例展示
   - 领域术语和概念介绍

2. **`run_cypher_query`** - Cypher 查询执行器
   - 安全的只读查询执行
   - 丰富的查询结果格式化
   - 智能错误提示和建议
   - 支持参数化查询

### 📊 知识图谱内容

- **企业管理** (Unternehmensführung)
- **创新发展** (Innovation)
- **企业传承** (Nachfolge)
- **治理结构** (Governance)
- **中小企业** (Mittelstand)
- **数字化转型** (Digitalisierung)

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Neo4j 5.0+
- 支持 MCP 的 AI 客户端 (Claude Desktop, Cursor, Cline 等)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/guangxiangdebizi/KnowledgeGraph-MCP.git
   cd KnowledgeGraph-MCP
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r mcp_requirements.txt
   ```

4. **配置 Neo4j 数据库**
   ```bash
   # 确保 Neo4j 服务运行在 localhost:7687
   # 修改 neo4j_mcp_server.py 中的连接配置
   NEO4J_URI = "bolt://localhost:7687"
   NEO4J_USERNAME = "neo4j"
   NEO4J_PASSWORD = "your_password"
   ```

5. **导入知识图谱数据**
   ```bash
   python import_to_neo4j.py
   ```

6. **启动 MCP 服务器**
   ```bash
   python neo4j_mcp_server.py
   ```

### MCP 客户端配置

#### Cursor
在 Cursor 的 MCP 配置中添加：
```json
{
  "mcpServers": {
    "neo4j-knowledge-graph": {
      "url": "http://127.0.0.1:8000/sse",
      "name": "Neo4j知识图谱",
      "description": "德国家族企业知识图谱查询服务"
    }
  }
}
```

#### Claude Desktop
在 `~/.config/claude/mcp_servers.json` 中添加：
```json
{
  "mcpServers": {
    "neo4j-knowledge-graph": {
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse",
      "name": "Neo4j知识图谱"
    }
  }
}
```

## 📁 项目结构

```
KnowledgeGraph-MCP/
├── neo4j_mcp_server.py           # MCP 服务器主程序
├── import_to_neo4j.py            # 数据导入脚本
├── setup_graphrag.py             # GraphRAG 设置脚本
├── mcp_requirements.txt          # MCP 依赖包
├── requirements.txt              # 完整依赖包
├── knowledge_graph_nodes.csv     # 节点数据
├── knowledge_graph_relationships.csv # 关系数据
├── 德国的家族企业/                # 原始文档
├── 德国的家族企业的PPT/           # 演示文档
├── README_MCP服务器使用说明.md    # MCP 使用说明
├── README_Neo4j导入说明.md       # 数据导入说明
├── cursor_config.json           # Cursor MCP 配置
├── cline_config.json            # Cline MCP 配置
└── 通用_mcp_config.json          # 通用 MCP 配置
```

## 💡 使用示例

### 1. 获取数据库结构
```python
# AI 首先调用此工具了解知识图谱结构
explain_database_structure()
```

### 2. 查询特定主题
```python
# AI 根据结构信息构造查询
run_cypher_query("""
MATCH (n:Node) 
WHERE n.name CONTAINS '创新' AND n.type = 'section'
RETURN n.name, n.description 
LIMIT 5
""")
```

### 3. 探索关系网络
```python
# 查找层次关系
run_cypher_query("""
MATCH (parent)-[:INCLUDES]->(child)
WHERE parent.name CONTAINS '家族企业'
RETURN parent.name, child.name, child.type
""")
```

## 🛠️ 技术栈

- **后端框架**: [FastMCP 2.0](https://github.com/jlowin/fastmcp)
- **图数据库**: [Neo4j 5.0+](https://neo4j.com)
- **Python 驱动**: [neo4j-driver](https://github.com/neo4j/neo4j-python-driver)
- **协议标准**: [Model Context Protocol](https://modelcontextprotocol.io)
- **传输方式**: Server-Sent Events (SSE)

## 📖 相关文档

- [MCP 服务器使用说明](README_MCP服务器使用说明.md)
- [Neo4j 数据导入说明](README_Neo4j导入说明.md)
- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [FastMCP 框架文档](https://gofastmcp.com)

## 🤝 贡献指南

我们欢迎各种形式的贡献！

1. **Fork** 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 **Pull Request**

### 贡献方向

- 🔍 扩展知识图谱数据内容
- 🛠️ 增强查询功能和性能
- 📚 完善文档和示例
- 🐛 修复 Bug 和改进代码质量
- 🌐 多语言支持

## ⚠️ 注意事项

- 确保 Neo4j 数据库正常运行
- MCP 服务器默认运行在 `http://127.0.0.1:8000`
- 所有查询都是只读的，不支持数据修改操作
- 建议在生产环境中配置适当的安全措施

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🙏 致谢

- [Neo4j](https://neo4j.com) - 提供强大的图数据库支持
- [FastMCP](https://github.com/jlowin/fastmcp) - 优秀的 MCP 框架
- [Model Context Protocol](https://modelcontextprotocol.io) - 标准化的 AI 上下文协议

## 📞 联系方式

如有问题或建议，请：

- 📧 提交 [Issue](https://github.com/guangxiangdebizi/KnowledgeGraph-MCP/issues)
- 💬 发起 [Discussion](https://github.com/guangxiangdebizi/KnowledgeGraph-MCP/discussions)
- ⭐ 给项目点个 Star 支持我们！

---

**让 AI 助手成为德国家族企业知识领域的专家！** 🚀 
