# Neo4j知识图谱MCP服务器使用说明

## 概述

这个MCP（Model Context Protocol）服务器专门用于与Neo4j图数据库交互，让大模型能够访问和查询德国家族企业知识图谱数据。

## 功能特性

### 🔍 核心查询功能
- **节点搜索**: 根据名称、类型或关键词搜索节点
- **节点详情**: 获取指定节点的完整信息和相关关系
- **关系查找**: 查找节点之间的关系
- **路径查找**: 查找两个节点之间的路径
- **邻居获取**: 获取指定节点的邻居节点

### 📊 分析功能
- **图结构分析**: 获取知识图谱的整体结构信息
- **中心性分析**: 分析节点在图中的重要性
- **全文搜索**: 在节点描述中进行全文搜索
- **模式信息**: 获取数据库的节点标签、关系类型等

### 🛠 高级功能
- **自定义Cypher查询**: 支持执行安全的Cypher查询语句
- **批量数据处理**: 高效处理大量图数据
- **错误处理**: 完善的错误处理和日志记录

## 安装配置

### 1. 安装依赖

```bash
pip install -r mcp_requirements.txt
```

### 2. 确保Neo4j运行

确保你的Neo4j数据库正在运行，并且已经导入了知识图谱数据：

```bash
# 检查Neo4j状态
neo4j status

# 如果未运行，启动Neo4j
neo4j start
```

### 3. 配置数据库连接

在 `neo4j_mcp_server.py` 中修改数据库连接参数：

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "chenxingyu"  # 修改为你的密码
```

### 4. 测试连接

```bash
python neo4j_mcp_server.py
```

## MCP工具列表

### 1. search_nodes
**功能**: 搜索节点
**参数**:
- `query` (必需): 搜索关键词
- `node_type` (可选): 节点类型过滤
- `limit` (可选): 结果数量限制，默认10

**示例**:
```json
{
  "query": "家族企业",
  "node_type": "section",
  "limit": 5
}
```

### 2. get_node_details
**功能**: 获取节点详情
**参数**:
- `node_id` (必需): 节点ID

**示例**:
```json
{
  "node_id": "part_1"
}
```

### 3. find_relationships
**功能**: 查找关系
**参数**:
- `source_node` (必需): 源节点ID或名称
- `target_node` (可选): 目标节点ID或名称
- `relationship_type` (可选): 关系类型过滤
- `direction` (可选): 关系方向 (incoming/outgoing/both)

**示例**:
```json
{
  "source_node": "part_1",
  "direction": "outgoing",
  "relationship_type": "INCLUDES"
}
```

### 4. find_paths
**功能**: 查找路径
**参数**:
- `start_node` (必需): 起始节点
- `end_node` (必需): 结束节点
- `max_depth` (可选): 最大路径深度，默认5
- `path_type` (可选): 路径类型 (shortest/all)

**示例**:
```json
{
  "start_node": "root",
  "end_node": "part_1_1",
  "max_depth": 3,
  "path_type": "shortest"
}
```

### 5. get_graph_structure
**功能**: 获取图结构
**参数**:
- `include_stats` (可选): 是否包含统计信息，默认true

**示例**:
```json
{
  "include_stats": true
}
```

### 6. get_neighbors
**功能**: 获取邻居节点
**参数**:
- `node_id` (必需): 节点ID或名称
- `depth` (可选): 邻居深度，默认1
- `relationship_type` (可选): 关系类型过滤

**示例**:
```json
{
  "node_id": "part_1",
  "depth": 2,
  "relationship_type": "INCLUDES"
}
```

### 7. full_text_search
**功能**: 全文搜索
**参数**:
- `search_text` (必需): 搜索文本
- `limit` (可选): 结果数量限制，默认10

**示例**:
```json
{
  "search_text": "创新",
  "limit": 15
}
```

### 8. run_cypher_query
**功能**: 执行Cypher查询
**参数**:
- `query` (必需): Cypher查询语句
- `parameters` (可选): 查询参数

**注意**: 出于安全考虑，不允许执行修改数据的查询（DELETE、CREATE等）

**示例**:
```json
{
  "query": "MATCH (n:Node {type: $type}) RETURN n.name, n.description LIMIT 5",
  "parameters": {"type": "section"}
}
```

### 9. get_schema_info
**功能**: 获取模式信息
**参数**: 无

### 10. analyze_centrality
**功能**: 中心性分析
**参数**:
- `algorithm` (可选): 中心性算法 (degree/betweenness/closeness)
- `limit` (可选): 结果数量限制，默认10

**示例**:
```json
{
  "algorithm": "degree",
  "limit": 10
}
```

## 使用场景示例

### 场景1: 探索知识图谱结构
```
1. 使用 get_graph_structure 获取整体结构
2. 使用 search_nodes 搜索感兴趣的节点
3. 使用 get_node_details 查看节点详情
4. 使用 get_neighbors 探索相关节点
```

### 场景2: 查找特定信息
```
1. 使用 full_text_search 搜索关键词
2. 使用 find_relationships 查看节点关系
3. 使用 find_paths 找到信息路径
```

### 场景3: 分析图结构
```
1. 使用 analyze_centrality 找到重要节点
2. 使用 get_schema_info 了解数据模式
3. 使用 run_cypher_query 执行复杂分析
```

## 常用查询示例

### 查找所有部分节点
```json
{
  "query": "MATCH (n:Node {type: 'section'}) RETURN n.name, n.id ORDER BY n.name",
  "parameters": {}
}
```

### 查找包含特定关键词的内容
```json
{
  "search_text": "创新",
  "limit": 10
}
```

### 分析节点重要性
```json
{
  "algorithm": "degree",
  "limit": 20
}
```

### 查找两个概念之间的关系
```json
{
  "start_node": "part_3",
  "end_node": "part_5",
  "max_depth": 4,
  "path_type": "shortest"
}
```

## 性能优化建议

1. **限制结果数量**: 对于大型查询，使用 `limit` 参数限制结果数量
2. **使用具体查询**: 尽量使用具体的节点ID而不是名称搜索
3. **缓存结果**: 对于重复查询，考虑缓存结果
4. **索引优化**: 确保Neo4j数据库有适当的索引

## 错误处理

服务器包含完善的错误处理机制：
- 数据库连接错误
- 查询语法错误
- 安全检查（防止危险操作）
- 参数验证错误

所有错误都会返回详细的错误信息，便于调试。

## 安全特性

1. **查询限制**: 不允许执行修改数据的查询
2. **参数验证**: 严格验证输入参数
3. **连接安全**: 使用安全的数据库连接
4. **日志记录**: 详细的操作日志

## 日志和监控

服务器会记录详细的操作日志，包括：
- 连接状态
- 查询执行
- 错误信息
- 性能统计

日志级别可以通过修改 `logging.basicConfig` 进行调整。

## 故障排除

### 常见问题

1. **连接失败**
   - 检查Neo4j服务是否运行
   - 验证连接参数是否正确
   - 检查网络连接

2. **查询无结果**
   - 检查数据是否已正确导入
   - 验证查询语法
   - 使用更宽泛的搜索条件

3. **性能问题**
   - 限制查询结果数量
   - 优化Cypher查询
   - 检查数据库索引

### 调试技巧

1. 使用 `get_schema_info` 了解数据结构
2. 使用简单查询测试连接
3. 检查日志文件获取详细错误信息
4. 使用Neo4j浏览器验证数据

## 扩展开发

如需添加新功能，可以：

1. 在 `list_tools()` 中添加新工具定义
2. 在 `call_tool()` 中添加工具调用处理
3. 实现具体的工具函数
4. 更新文档和示例

## 联系支持

如遇到问题，请检查：
1. Neo4j数据库状态
2. Python依赖是否完整
3. 配置参数是否正确
4. 日志文件中的错误信息

---

*本MCP服务器为德国家族企业知识图谱项目的一部分，提供强大的图数据库查询能力。* 