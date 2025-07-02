# 德国家族企业知识图谱 - Neo4j导入说明

## 📋 项目简介

本项目将德国家族企业相关的文档内容整理成知识图谱，并提供完整的Neo4j数据库导入解决方案。

## 🗄️ 数据结构

### 节点信息
- **id**: 节点唯一标识符
- **name**: 节点名称
- **description**: 节点详细描述
- **type**: 节点类型（第一部分、第二部分等）

### 关系类型
- **CONTAINS**: 包含关系（上级包含下级）
- **INCLUDES**: 包括关系（部分包括细节）

## 🚀 快速开始

### 1. 前置条件

#### 安装Neo4j
```bash
# 使用Docker安装Neo4j（推荐）
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

或者从官网下载安装：https://neo4j.com/download/

#### 验证Neo4j安装
1. 打开浏览器访问：http://localhost:7474
2. 使用用户名 `neo4j` 和密码 `password` 登录

### 2. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库连接

编辑 `import_to_neo4j.py` 文件中的连接参数：

```python
# Neo4j连接配置
NEO4J_URI = "bolt://localhost:7687"  # 您的Neo4j地址
NEO4J_USERNAME = "neo4j"             # 您的用户名
NEO4J_PASSWORD = "your_password"     # 您的密码
```

### 4. 执行导入

```bash
python import_to_neo4j.py
```

程序会询问是否清空现有数据库，按需选择。

## 📊 数据验证

导入完成后，您可以在Neo4j Browser中执行以下查询来验证数据：

### 基础查询
```cypher
// 查看所有节点（限制25个）
MATCH (n:KnowledgeNode) RETURN n LIMIT 25

// 统计节点总数
MATCH (n:KnowledgeNode) RETURN count(n) as total_nodes

// 统计关系总数
MATCH ()-[r]->() RETURN count(r) as total_relationships
```

### 层次结构查询
```cypher
// 查看根节点和第一层子节点
MATCH (root {id: 'root'})-[:CONTAINS]->(child) 
RETURN root, child

// 查看完整的2层层次结构
MATCH (root {id: 'root'})-[:CONTAINS]->(part)-[:INCLUDES]->(detail)
RETURN root, part, detail

// 查看特定部分的内容
MATCH (n:KnowledgeNode) 
WHERE n.type = '第一部分' 
RETURN n
```

### 内容搜索查询
```cypher
// 搜索包含特定关键词的节点
MATCH (n:KnowledgeNode) 
WHERE n.description CONTAINS '家族企业'
RETURN n.name, n.description
LIMIT 10

// 查找匡特家族相关内容
MATCH (n:KnowledgeNode) 
WHERE n.name CONTAINS '匡特' OR n.description CONTAINS '匡特'
RETURN n
```

### 统计分析查询
```cypher
// 按类型统计节点数量
MATCH (n:KnowledgeNode) 
RETURN n.type as type, count(n) as count 
ORDER BY count DESC

// 查看每个部分包含的子节点数量
MATCH (part)-[:INCLUDES]->(detail)
RETURN part.name, count(detail) as detail_count
ORDER BY detail_count DESC
```

## 🔍 知识图谱探索

### 可视化查询
```cypher
// 展示完整的知识图谱结构（小规模）
MATCH p=(root {id: 'root'})-[:CONTAINS*1..2]->(n)
RETURN p
LIMIT 50

// 展示德国家族企业特征
MATCH (root)-[:CONTAINS]->(part {name: '第三部分 德国家族企业特征综述'})-[:INCLUDES]->(char)
RETURN part, char

// 展示匡特家族的故事线
MATCH (n:KnowledgeNode) 
WHERE n.type IN ['第十三部分', '第十四部分']
RETURN n
```

### 路径查询
```cypher
// 查找从根节点到某个具体概念的路径
MATCH path = (root {id: 'root'})-[:CONTAINS*]->(target)
WHERE target.name CONTAINS '创新'
RETURN path
LIMIT 5

// 查找相关概念之间的关系
MATCH (n1:KnowledgeNode)-[r]-(n2:KnowledgeNode)
WHERE n1.description CONTAINS '财务' AND n2.description CONTAINS '财务'
RETURN n1, r, n2
```

## 🛠️ 故障排除

### 常见问题

1. **连接失败**
   - 检查Neo4j是否正在运行
   - 验证连接参数（URI、用户名、密码）
   - 确认端口7687未被占用

2. **导入错误**
   - 确认CSV文件编码为UTF-8
   - 检查文件路径是否正确
   - 验证CSV文件格式

3. **内存不足**
   - 增加Neo4j内存配置
   - 减小批处理大小（修改batch_size参数）

### 性能优化

```cypher
// 创建额外索引（如需要）
CREATE INDEX IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.description)

// 查看当前索引
SHOW INDEXES
```

## 📈 后续使用建议

1. **定期备份**
   ```bash
   # 备份数据库
   neo4j-admin dump --database=neo4j --to=/path/to/backup.dump
   ```

2. **性能监控**
   - 使用Neo4j Browser的查询分析器
   - 监控查询执行时间
   - 优化复杂查询

3. **扩展功能**
   - 集成APOC插件获得更多功能
   - 考虑使用Graph Data Science库进行图分析
   - 开发Web应用程序进行知识图谱可视化

## 📚 参考资源

- [Neo4j官方文档](https://neo4j.com/docs/)
- [Cypher查询语言指南](https://neo4j.com/developer/cypher/)
- [APOC插件文档](https://neo4j.com/labs/apoc/)

---

如有问题，请检查日志输出或联系技术支持。 