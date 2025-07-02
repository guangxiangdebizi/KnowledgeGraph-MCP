#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
德国家族企业知识图谱数据导入Neo4j数据库
Author: Assistant
Date: 2024
"""

import pandas as pd
from neo4j import GraphDatabase
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jImporter:
    """Neo4j数据导入类"""
    
    def __init__(self, uri: str, username: str, password: str):
        """
        初始化Neo4j连接
        
        Args:
            uri: Neo4j数据库URI (例如: "bolt://localhost:7687")
            username: 用户名 (默认: "neo4j")
            password: 密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"成功连接到Neo4j数据库: {uri}")
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("数据库连接已关闭")
    
    def clear_database(self):
        """清空数据库（可选操作）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("数据库已清空")
    
    def create_constraints(self):
        """创建约束和索引"""
        constraints = [
            "CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:KnowledgeNode) REQUIRE n.id IS UNIQUE",
            "CREATE INDEX node_name_index IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.name)",
            "CREATE INDEX node_type_index IF NOT EXISTS FOR (n:KnowledgeNode) ON (n.type)"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"成功创建约束/索引: {constraint}")
                except Exception as e:
                    logger.warning(f"约束/索引可能已存在: {e}")
    
    def import_nodes(self, nodes_file: str):
        """
        导入节点数据
        
        Args:
            nodes_file: 节点CSV文件路径
        """
        try:
            # 读取CSV文件
            nodes_df = pd.read_csv(nodes_file, encoding='utf-8')
            logger.info(f"成功读取节点文件: {nodes_file}, 共{len(nodes_df)}个节点")
            
            # 批量导入节点
            batch_size = 100
            total_batches = (len(nodes_df) + batch_size - 1) // batch_size
            
            with self.driver.session() as session:
                for i in range(0, len(nodes_df), batch_size):
                    batch = nodes_df[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    
                    # 准备批次数据
                    nodes_data = []
                    for _, row in batch.iterrows():
                        nodes_data.append({
                            'id': row['id'],
                            'name': row['name'],
                            'description': row['description'],
                            'type': row['type']
                        })
                    
                    # 执行批量插入
                    query = """
                    UNWIND $nodes_data AS node
                    CREATE (n:KnowledgeNode {
                        id: node.id,
                        name: node.name,
                        description: node.description,
                        type: node.type
                    })
                    """
                    
                    session.run(query, nodes_data=nodes_data)
                    logger.info(f"已导入节点批次 {batch_num}/{total_batches} ({len(batch)}个节点)")
            
            logger.info(f"所有节点导入完成！总计{len(nodes_df)}个节点")
            
        except Exception as e:
            logger.error(f"导入节点时发生错误: {e}")
            raise
    
    def import_relationships(self, relationships_file: str):
        """
        导入关系数据
        
        Args:
            relationships_file: 关系CSV文件路径
        """
        try:
            # 读取CSV文件
            relationships_df = pd.read_csv(relationships_file, encoding='utf-8')
            logger.info(f"成功读取关系文件: {relationships_file}, 共{len(relationships_df)}个关系")
            
            # 批量导入关系
            batch_size = 100
            total_batches = (len(relationships_df) + batch_size - 1) // batch_size
            
            with self.driver.session() as session:
                for i in range(0, len(relationships_df), batch_size):
                    batch = relationships_df[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    
                    # 准备批次数据
                    relationships_data = []
                    for _, row in batch.iterrows():
                        relationships_data.append({
                            'source_id': row['source_id'],
                            'target_id': row['target_id'],
                            'relationship_type': row['relationship_type'],
                            'description': row['description']
                        })
                    
                    # 执行批量创建关系
                    query = """
                    UNWIND $relationships_data AS rel
                    MATCH (source:KnowledgeNode {id: rel.source_id})
                    MATCH (target:KnowledgeNode {id: rel.target_id})
                    CALL apoc.create.relationship(source, rel.relationship_type, {
                        description: rel.description
                    }, target) YIELD rel as relationship
                    RETURN count(relationship)
                    """
                    
                    # 如果没有APOC插件，使用基础语法
                    fallback_query = """
                    UNWIND $relationships_data AS rel
                    MATCH (source:KnowledgeNode {id: rel.source_id})
                    MATCH (target:KnowledgeNode {id: rel.target_id})
                    CREATE (source)-[r:RELATED {
                        type: rel.relationship_type,
                        description: rel.description
                    }]->(target)
                    """
                    
                    try:
                        session.run(query, relationships_data=relationships_data)
                    except:
                        # 如果APOC不可用，使用fallback方案
                        session.run(fallback_query, relationships_data=relationships_data)
                    
                    logger.info(f"已导入关系批次 {batch_num}/{total_batches} ({len(batch)}个关系)")
            
            logger.info(f"所有关系导入完成！总计{len(relationships_df)}个关系")
            
        except Exception as e:
            logger.error(f"导入关系时发生错误: {e}")
            raise
    
    def create_hierarchy_relationships(self):
        """创建特定的层次关系（CONTAINS和INCLUDES）"""
        queries = [
            # 创建CONTAINS关系
            """
            MATCH (source:KnowledgeNode)-[r:RELATED]->(target:KnowledgeNode)
            WHERE r.type = 'CONTAINS'
            CREATE (source)-[:CONTAINS {description: r.description}]->(target)
            """,
            # 创建INCLUDES关系
            """
            MATCH (source:KnowledgeNode)-[r:RELATED]->(target:KnowledgeNode)
            WHERE r.type = 'INCLUDES'
            CREATE (source)-[:INCLUDES {description: r.description}]->(target)
            """,
            # 删除通用RELATED关系
            """
            MATCH ()-[r:RELATED]->()
            DELETE r
            """
        ]
        
        with self.driver.session() as session:
            for query in queries:
                session.run(query)
            logger.info("已创建层次关系并清理通用关系")
    
    def verify_import(self):
        """验证导入结果"""
        with self.driver.session() as session:
            # 统计节点数量
            node_count = session.run("MATCH (n:KnowledgeNode) RETURN count(n) as count").single()["count"]
            
            # 统计关系数量
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            # 按类型统计节点
            type_stats = session.run("""
                MATCH (n:KnowledgeNode) 
                RETURN n.type as type, count(n) as count 
                ORDER BY count DESC
            """)
            
            logger.info(f"导入验证结果:")
            logger.info(f"- 总节点数: {node_count}")
            logger.info(f"- 总关系数: {rel_count}")
            logger.info(f"- 按类型统计:")
            
            for record in type_stats:
                logger.info(f"  {record['type']}: {record['count']}个节点")

def main():
    """主函数"""
    # Neo4j连接配置
    NEO4J_URI = "bolt://localhost:7687"  # 根据实际情况修改
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "chenxingyu"  # 请修改为您的密码
    
    # CSV文件路径
    NODES_FILE = "knowledge_graph_nodes.csv"
    RELATIONSHIPS_FILE = "knowledge_graph_relationships.csv"
    
    importer = None
    try:
        # 创建导入器实例
        importer = Neo4jImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        # 询问是否清空数据库
        clear_db = input("是否清空现有数据库? (y/N): ").lower().strip()
        if clear_db == 'y':
            importer.clear_database()
        
        # 创建约束和索引
        importer.create_constraints()
        
        # 导入节点
        logger.info("开始导入节点...")
        importer.import_nodes(NODES_FILE)
        
        # 导入关系
        logger.info("开始导入关系...")
        importer.import_relationships(RELATIONSHIPS_FILE)
        
        # 创建层次关系
        logger.info("创建层次关系...")
        importer.create_hierarchy_relationships()
        
        # 验证导入结果
        logger.info("验证导入结果...")
        importer.verify_import()
        
        logger.info("🎉 德国家族企业知识图谱导入完成！")
        logger.info("💡 您可以在Neo4j Browser中使用以下查询语句探索数据：")
        logger.info("   - 查看所有节点: MATCH (n) RETURN n LIMIT 25")
        logger.info("   - 查看根节点及其子节点: MATCH (root {id: 'root'})-[:CONTAINS]->(child) RETURN root, child")
        logger.info("   - 按类型查看节点: MATCH (n:KnowledgeNode) WHERE n.type = '第一部分' RETURN n")
        
    except Exception as e:
        logger.error(f"导入过程中发生错误: {e}")
        return 1
    
    finally:
        if importer:
            importer.close()
    
    return 0

if __name__ == "__main__":
    exit(main()) 