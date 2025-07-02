#!/usr/bin/env python3
"""
Neo4j MCP Server - 专门用于与Neo4j图数据库交互的MCP服务器
使用FastMCP 2.0实现，支持SSE传输协议
提供核心的Cypher查询和数据库结构解释功能
"""

import json
import logging
from typing import Dict, List, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# 使用新版本的FastMCP
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Neo4j连接配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "chenxingyu"

class Neo4jDatabase:
    """Neo4j数据库连接管理"""
    
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        
    def connect(self):
        """连接到Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            # 测试连接
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
    
    def run_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """执行Cypher查询"""
        if not self.driver:
            raise Exception("Not connected to Neo4j database")
        
        try:
                with self.driver.session() as session:
                    result = session.run(query, parameters or {})
                    return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

# 初始化数据库连接
db = Neo4jDatabase(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

# 创建FastMCP实例
mcp = FastMCP("Neo4j知识图谱")

@mcp.tool()
def run_cypher_query(query: str, parameters: Optional[Dict] = None) -> str:
    """执行自定义Cypher查询语句
    
    允许执行任何只读的Cypher查询来探索和分析知识图谱数据。
    出于安全考虑，不允许执行修改数据的操作（CREATE、DELETE、SET等）。
    
    Args:
        query: 要执行的Cypher查询语句，支持MATCH、RETURN、WITH、WHERE等只读操作
        parameters: 查询参数字典，用于参数化查询以提高安全性和性能
    
    Returns:
        查询结果的格式化文本，包含所有字段和记录数据
    
    Examples:
        - 搜索节点: "MATCH (n:Node) WHERE n.name CONTAINS '家族企业' RETURN n LIMIT 5"
        - 查找关系: "MATCH (a)-[r]->(b) WHERE a.id = 'part_1' RETURN type(r), b.name"
        - 统计信息: "MATCH (n:Node) RETURN n.type, count(n) as count ORDER BY count DESC"
    """
    if not query.strip():
        return "错误：查询语句不能为空"
    
    # 安全检查，避免危险操作
    dangerous_keywords = ["DELETE", "REMOVE", "DROP", "CREATE", "MERGE", "SET", "DETACH"]
    query_upper = query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return f"错误：出于安全考虑，不允许执行包含 '{keyword}' 的查询。请使用只读操作如MATCH、RETURN、WHERE等。"
    
    try:
        results = db.run_query(query, parameters or {})
        
        if not results:
            return "查询成功执行，但未返回任何结果。"
        
        # 格式化结果
        response = f"✅ 查询成功！共返回 {len(results)} 条记录：\n\n"
        
        # 获取字段名
        if results:
            fields = list(results[0].keys())
            response += f"📋 字段: {', '.join(fields)}\n\n"
            
            # 限制显示记录数量以避免输出过长
            display_limit = min(len(results), 20)
            
            for i, record in enumerate(results[:display_limit], 1):
                response += f"📍 记录 {i}:\n"
                for field in fields:
                    value = record.get(field, "")
                    
                    # 处理复杂数据类型
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False, indent=2)
                    elif isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    
                    response += f"  • {field}: {value}\n"
                response += "\n"
            
            if len(results) > display_limit:
                response += f"... 还有 {len(results) - display_limit} 条记录未显示（为避免输出过长）\n"
        
        return response
        
    except Exception as e:
        return f"❌ 查询执行失败: {str(e)}\n\n💡 提示：请检查Cypher语法是否正确，确保引用的节点、关系和属性名称存在。"

@mcp.tool()
def explain_database_structure() -> str:
    """解释德国家族企业知识图谱的完整结构和schema信息
    
    提供详细的数据库结构概览，包括节点类型、关系类型、属性信息、实际数据样例等，
    让AI助手能够立即理解整个知识图谱的组织结构并自然地构造Cypher查询。
    
    Returns:
        知识图谱的完整结构说明，包含所有必要信息用于智能查询构造
    """
    try:
        structure_info = []
        
        # 添加知识图谱的领域背景
        structure_info.extend([
            "🏢 德国家族企业知识图谱数据库",
            "=" * 50,
            "",
            "📖 数据库简介:",
            "本数据库包含德国家族企业相关的结构化知识，涵盖企业管理、创新、传承、",
            "治理结构等多个维度的内容。数据按照层次化结构组织。",
            "",
        ])
        
        # 1. 获取基本统计信息
        stats_query = """
        MATCH (n)
        WITH count(n) as total_nodes
        MATCH ()-[r]->()
        WITH total_nodes, count(r) as total_relationships
        RETURN total_nodes, total_relationships
        """
        stats = db.run_query(stats_query)
        
        if stats:
            structure_info.extend([
                "📊 数据库统计:",
                f"  • 节点总数: {stats[0]['total_nodes']:,}",
                f"  • 关系总数: {stats[0]['total_relationships']:,}",
                "",
            ])
        
        # 2. 详细的节点标签信息和示例
        labels_query = """
        CALL db.labels() YIELD label
        RETURN collect(label) as labels
        """
        labels_result = db.run_query(labels_query)
        
        if labels_result and labels_result[0]['labels']:
            structure_info.append("🏷️ 节点类型详情:")
            structure_info.append("")
            
            for label in labels_result[0]['labels']:
                # 获取每个标签的节点数量
                count_query = f"MATCH (n:{label}) RETURN count(n) as count"
                count_result = db.run_query(count_query)
                count = count_result[0]['count'] if count_result else 0
                
                structure_info.append(f"📌 {label} 类型 ({count:,} 个节点)")
                
                # 获取该类型节点的属性信息
                props_query = f"""
                MATCH (n:{label})
                WITH keys(n) as node_keys
                UNWIND node_keys as key
                RETURN DISTINCT key, count(*) as frequency
                ORDER BY frequency DESC
                LIMIT 10
                """
                props_result = db.run_query(props_query)
                
                if props_result:
                    structure_info.append("  属性字段:")
                    for prop in props_result:
                        structure_info.append(f"    • {prop['key']} (出现在 {prop['frequency']} 个节点中)")
                
                # 获取该类型的具体数据示例
                example_query = f"MATCH (n:{label}) RETURN n LIMIT 3"
                examples = db.run_query(example_query)
                
                if examples:
                    structure_info.append("  数据样例:")
                    for i, example in enumerate(examples, 1):
                        node_data = example['n']
                        structure_info.append(f"    样例 {i}:")
                        # 重点显示name, type, description
                        important_fields = ['name', 'type', 'description']
                        for field in important_fields:
                            if field in node_data:
                                value = str(node_data[field])
                                if len(value) > 80:
                                    value = value[:80] + "..."
                                structure_info.append(f"      {field}: {value}")
                
                structure_info.append("")
        
        # 3. 详细的关系类型信息和示例
        rel_types_query = """
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN collect(relationshipType) as types
        """
        rel_types_result = db.run_query(rel_types_query)
        
        if rel_types_result and rel_types_result[0]['types']:
            structure_info.append("🔗 关系类型详情:")
            structure_info.append("")
            
            for rel_type in rel_types_result[0]['types']:
                # 获取每种关系类型的数量
                count_query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
                count_result = db.run_query(count_query)
                count = count_result[0]['count'] if count_result else 0
                
                structure_info.append(f"🔗 {rel_type} 关系 ({count:,} 个)")
                
                # 获取关系的具体示例和连接模式
                rel_example_query = f"""
                MATCH (a)-[r:{rel_type}]->(b)
                RETURN labels(a) as source_labels, a.name as source_name, a.type as source_type,
                       labels(b) as target_labels, b.name as target_name, b.type as target_type,
                       properties(r) as rel_props
                LIMIT 3
                """
                rel_examples = db.run_query(rel_example_query)
                
                if rel_examples:
                    structure_info.append("  连接模式和示例:")
                    for i, rel_ex in enumerate(rel_examples, 1):
                        source_label = rel_ex['source_labels'][0] if rel_ex['source_labels'] else 'Unknown'
                        target_label = rel_ex['target_labels'][0] if rel_ex['target_labels'] else 'Unknown'
                        structure_info.append(f"    示例 {i}: ({source_label})-[{rel_type}]->({target_label})")
                        structure_info.append(f"      源节点: {rel_ex['source_name']} (type: {rel_ex['source_type']})")
                        structure_info.append(f"      目标节点: {rel_ex['target_name']} (type: {rel_ex['target_type']})")
                        
                        if rel_ex['rel_props']:
                            structure_info.append(f"      关系属性: {rel_ex['rel_props']}")
                
                structure_info.append("")
        
        # 4. 数据组织层次结构
        structure_info.extend([
            "📋 数据组织层次:",
            "",
            "根据数据样例，知识图谱采用层次化组织结构：",
        ])
        
        # 获取层次结构信息
        hierarchy_query = """
        MATCH (n:Node)
        WHERE n.type IS NOT NULL
        RETURN DISTINCT n.type as node_type, count(n) as count
        ORDER BY count DESC
        """
        hierarchy_result = db.run_query(hierarchy_query)
        
        if hierarchy_result:
            structure_info.append("  节点类型分布:")
            for hier in hierarchy_result:
                structure_info.append(f"    • {hier['node_type']}: {hier['count']} 个节点")
            structure_info.append("")
        
        # 5. 获取具体的节点名称样例帮助理解内容结构
        name_pattern_query = """
        MATCH (n:Node)
        WHERE n.name IS NOT NULL AND n.type IS NOT NULL
        RETURN DISTINCT n.name, n.type
        ORDER BY n.type, n.name
        LIMIT 20
        """
        name_patterns = db.run_query(name_pattern_query)
        
        if name_patterns:
            structure_info.extend([
                "📝 节点名称和类型样例:",
                ""
            ])
            
            current_type = None
            for pattern in name_patterns:
                if pattern['type'] != current_type:
                    current_type = pattern['type']
                    structure_info.append(f"  {pattern['type']} 类型:")
                structure_info.append(f"    • {pattern['name']}")
            
            structure_info.append("")
        
        # 6. 关键领域术语
        structure_info.extend([
            "📚 德国家族企业关键概念:",
            "",
            "• Familienunternehmen: 家族企业",
            "• Innovation: 创新",
            "• Nachfolge: 企业传承",
            "• Governance: 治理结构", 
            "• Mittelstand: 中小企业",
            "• Unternehmensführung: 企业管理",
            "• Digitalisierung: 数字化",
            "",
            "🎯 推荐查询方式:",
            "• 使用 n.name CONTAINS '关键词' 进行内容搜索",
            "• 使用 n.type = '类型名' 进行精确类型过滤",
            "• 结合 WHERE n.type = '类型' AND n.name CONTAINS '关键词'",
            "• description字段包含详细内容，适合全文搜索",
            "• 关系查询使用节点的name和type字段进行定位",
            "",
            "现在你可以使用 run_cypher_query 工具基于以上结构信息构造查询！",
            "="*50
        ])
        
        return "\n".join(structure_info)
        
    except Exception as e:
        return f"❌ 获取数据库结构信息失败: {str(e)}\n\n💡 请确保数据库连接正常且包含德国家族企业知识图谱数据。"

def main():
    """主函数"""
    try:
        # 连接数据库
        db.connect()
        logger.info("Neo4j MCP Server initialized successfully")
        
        # 使用FastMCP 2.0的方式运行SSE服务器
        logger.info("Starting Neo4j MCP Server on http://127.0.0.1:8000")
        mcp.run(transport="sse", host="127.0.0.1", port=8000)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}") 
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 