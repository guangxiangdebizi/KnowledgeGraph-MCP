#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microsoft GraphRAG 设置脚本
将德国家族企业文档转换为GraphRAG知识图谱
"""

import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraphRAGSetup:
    def __init__(self, project_name="german_family_business"):
        self.project_name = project_name
        self.base_dir = Path.cwd()
        self.project_dir = self.base_dir / project_name
        self.input_dir = self.project_dir / "input"
        
    def create_project_structure(self):
        """创建GraphRAG项目结构"""
        logger.info("创建GraphRAG项目结构...")
        
        # 创建项目目录
        self.project_dir.mkdir(exist_ok=True)
        self.input_dir.mkdir(exist_ok=True)
        
        # 创建输出目录
        (self.project_dir / "output").mkdir(exist_ok=True)
        (self.project_dir / "prompts").mkdir(exist_ok=True)
        
        logger.info(f"项目目录创建完成: {self.project_dir}")
        
    def copy_documents(self):
        """复制德国家族企业文档到input目录"""
        logger.info("复制文档到GraphRAG input目录...")
        
        source_dir = self.base_dir / "德国的家族企业"
        
        if not source_dir.exists():
            logger.error(f"源文档目录不存在: {source_dir}")
            return
            
        # 复制所有txt文件
        txt_files = list(source_dir.glob("*.txt"))
        
        for txt_file in txt_files:
            dest_file = self.input_dir / txt_file.name
            shutil.copy2(txt_file, dest_file)
            logger.info(f"已复制: {txt_file.name}")
            
        logger.info(f"共复制了 {len(txt_files)} 个文档文件")
        
    def create_settings_yaml(self):
        """创建GraphRAG配置文件"""
        logger.info("创建GraphRAG配置文件...")
        
        settings_content = """
# GraphRAG Configuration for German Family Business Knowledge Graph
# 德国家族企业知识图谱配置

# LLM Configuration
llm:
  api_key: ${GRAPHRAG_API_KEY}
  type: openai_chat # or azure_openai_chat
  model: gpt-4o-mini
  model_supports_json: true
  max_tokens: 4000
  temperature: 0.1
  top_p: 1.0
  n: 1

# Embeddings Configuration  
embeddings:
  api_key: ${GRAPHRAG_API_KEY}
  type: openai_embedding # or azure_openai_embedding
  model: text-embedding-3-small
  max_tokens: 8191

# Input Configuration
input:
  type: file
  file_type: text
  base_dir: "input"
  file_encoding: utf-8
  file_pattern: ".*\\.txt$"

# Storage Configuration
storage:
  type: file
  base_dir: "output"

# Cache Configuration
cache:
  type: file
  base_dir: "cache"

# Reporting Configuration
reporting:
  type: file
  base_dir: "output/reports"

# Entity Extraction
entity_extraction:
  entity_types: [组织, 人物, 概念, 地点, 时间, 数据, 特征, 案例, 策略, 制度]
  max_gleanings: 1
  
# Claim Extraction
claim_extraction:
  enabled: true
  max_gleanings: 1

# Community Summarization
community_summarization:
  max_length: 2000

# Chinese Language Support
encoding: utf-8

# Chunk Configuration
chunks:
  size: 1200
  overlap: 100
  group_by_columns: [id]

# Snapshots
snapshots:
  graphml: true
  raw_entities: true
  raw_relationships: true
  top_level_nodes: true

# Local Search
local_search:
  text_unit_prop: 0.5
  community_prop: 0.1
  conversation_history_max_turns: 5
  top_k_entities: 10
  top_k_relationships: 10
  max_tokens: 12000

# Global Search  
global_search:
  max_tokens: 12000
  data_max_tokens: 12000
  map_max_tokens: 1000
  reduce_max_tokens: 2000
  concurrency: 32
"""
        
        settings_file = self.project_dir / "settings.yaml"
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(settings_content.strip())
            
        logger.info(f"配置文件已创建: {settings_file}")
        
    def create_env_template(self):
        """创建环境变量模板"""
        env_content = """# GraphRAG Environment Variables
# 请设置你的API密钥

# OpenAI API Key (推荐使用)
GRAPHRAG_API_KEY=your_openai_api_key_here

# 或者 Azure OpenAI (可选)
# GRAPHRAG_API_KEY=your_azure_openai_api_key_here
# AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here

# 如果使用代理
# HTTP_PROXY=http://your-proxy:port
# HTTPS_PROXY=http://your-proxy:port
"""
        
        env_file = self.project_dir / ".env.template"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content.strip())
            
        logger.info(f"环境变量模板已创建: {env_file}")
        logger.info("请复制 .env.template 为 .env 并设置你的API密钥")
        
    def create_installation_script(self):
        """创建安装脚本"""
        install_content = """#!/bin/bash
# GraphRAG 安装脚本

echo "安装Microsoft GraphRAG..."

# 安装GraphRAG
pip install graphrag

# 验证安装
python -c "import graphrag; print('GraphRAG安装成功!')"

echo "安装完成！"
echo ""
echo "下一步："
echo "1. 设置 .env 文件中的API密钥"
echo "2. 运行: python run_graphrag.py"
"""
        
        install_file = self.project_dir / "install.sh"
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(install_content.strip())
            
        # Windows批处理文件
        install_bat = """@echo off
echo 安装Microsoft GraphRAG...

pip install graphrag

python -c "import graphrag; print('GraphRAG安装成功!')"

echo 安装完成！
echo.
echo 下一步：
echo 1. 设置 .env 文件中的API密钥  
echo 2. 运行: python run_graphrag.py
pause
"""
        
        bat_file = self.project_dir / "install.bat"
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(install_bat.strip())
            
        logger.info("安装脚本已创建: install.sh 和 install.bat")
        
    def create_run_script(self):
        """创建运行脚本"""
        run_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
GraphRAG 运行脚本
\"\"\"

import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_graphrag_pipeline():
    \"\"\"运行GraphRAG完整流水线\"\"\"
    try:
        logger.info("开始运行GraphRAG流水线...")
        
        # 1. 索引构建
        logger.info("步骤1: 构建知识图谱索引...")
        result = subprocess.run([
            "python", "-m", "graphrag.index", 
            "--root", ".", 
            "--config", "settings.yaml"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"索引构建失败: {result.stderr}")
            return False
            
        logger.info("索引构建完成!")
        
        # 2. 验证输出
        output_dir = Path("output")
        if (output_dir / "artifacts").exists():
            logger.info("知识图谱构建成功!")
            logger.info(f"输出目录: {output_dir.absolute()}")
            
            # 显示生成的文件
            artifacts = list((output_dir / "artifacts").rglob("*"))
            logger.info(f"共生成 {len(artifacts)} 个文件")
            
        return True
        
    except Exception as e:
        logger.error(f"运行出错: {e}")
        return False

def run_query_example():
    \"\"\"运行查询示例\"\"\"
    try:
        logger.info("运行查询示例...")
        
        # 本地搜索示例
        local_query = "德国家族企业有哪些特征？"
        logger.info(f"本地搜索: {local_query}")
        
        result = subprocess.run([
            "python", "-m", "graphrag.query",
            "--root", ".",
            "--method", "local",
            "--query", local_query
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("查询结果:")
            print(result.stdout)
        else:
            logger.error(f"查询失败: {result.stderr}")
            
    except Exception as e:
        logger.error(f"查询出错: {e}")

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("GRAPHRAG_API_KEY"):
        logger.error("请设置GRAPHRAG_API_KEY环境变量")
        exit(1)
        
    # 运行流水线
    if run_graphrag_pipeline():
        logger.info("GraphRAG设置完成!")
        
        # 运行示例查询
        run_query_example()
    else:
        logger.error("GraphRAG运行失败")
"""
        
        run_file = self.project_dir / "run_graphrag.py"
        with open(run_file, 'w', encoding='utf-8') as f:
            f.write(run_content)
            
        logger.info(f"运行脚本已创建: {run_file}")
        
    def setup_complete_project(self):
        """设置完整的GraphRAG项目"""
        logger.info("开始设置GraphRAG项目...")
        
        self.create_project_structure()
        self.copy_documents()
        self.create_settings_yaml()
        self.create_env_template()
        self.create_installation_script()
        self.create_run_script()
        
        logger.info("=" * 50)
        logger.info("GraphRAG项目设置完成!")
        logger.info(f"项目目录: {self.project_dir}")
        logger.info("")
        logger.info("下一步操作:")
        logger.info("1. cd " + str(self.project_dir))
        logger.info("2. 运行安装脚本: install.bat (Windows) 或 ./install.sh (Linux/Mac)")
        logger.info("3. 复制 .env.template 为 .env 并设置API密钥")
        logger.info("4. 运行: python run_graphrag.py")
        logger.info("=" * 50)

def main():
    setup = GraphRAGSetup()
    setup.setup_complete_project()

if __name__ == "__main__":
    main() 