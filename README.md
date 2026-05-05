# KnowledgeWed - 知识图谱构建项目

基于非结构化文本构建知识图谱，并提供图谱查询和GraphRAG服务的后端项目。

## 项目简介

KnowledgeWed是一个完整的知识图谱构建系统，能够从非结构化文本中抽取实体和关系，链接到Wikidata知识库，存储到Neo4j图数据库，并通过FastAPI提供查询服务和GraphRAG能力。

## 核心功能

- **实体抽取**：使用智谱AI GLM-4.5模型从文本中抽取实体和关系
- **实体链接**：将抽取的实体链接到Wikidata，实现知识对齐
- **图谱存储**：将结构化数据导入Neo4j图数据库
- **API服务**：提供RESTful API接口进行图谱查询
- **GraphRAG**：将图谱知识转化为自然语言上下文，增强大模型问答

## 技术栈

- **Python** - 主要编程语言
- **FastAPI** (0.136.0) - Web框架
- **Neo4j** (6.1.0) - 图数据库
- **ZhipuAI** (zai 0.0.2) - 智谱AI SDK
- **Pydantic** (2.13.2) - 数据验证
- **Uvicorn** (0.44.0) - ASGI服务器

## 项目结构

```
KnowledgeWed/
├── data/
│   ├── input/              # 输入文本数据
│   │   └── turing_raw_data_zhcn.txt
│   └── output/             # 输出JSON数据
├── src/
│   ├── api.py              # FastAPI服务
│   ├── extractEntities.py  # 实体抽取
│   └── import_to_neo4j.py  # Neo4j导入
└── requirements.txt        # 依赖配置
```

## 环境要求

- Python 3.8+
- Neo4j 4.0+
- 智谱AI API密钥

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd KnowledgeWed
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
export ZAI_API_KEY="your-zhipu-api-key"
```

4. 启动Neo4j数据库
```bash
# 确保Neo4j运行在 neo4j://127.0.0.1:7687
```

## 使用方法

### 1. 实体抽取

将待处理的文本文件放入 `data/input/` 目录，然后运行：

```bash
python src/extractEntities.py
```

抽取结果将保存到 `data/output/` 目录。

### 2. 导入Neo4j

将抽取的JSON数据导入图数据库：

```bash
python src/import_to_neo4j.py
```

### 3. 启动API服务

```bash
python src/api.py
```

或使用uvicorn：

```bash
uvicorn src.api:app --host 127.0.0.1 --port 8000
```

服务启动后访问：
- API服务：http://127.0.0.1:8000
- API文档：http://127.0.0.1:8000/docs

## API接口

### 实体检索
```
GET /api/v1/search?name={entity_name}
```
根据名称或别名搜索实体。

### 图谱可视化
```
GET /api/v1/graph/all?limit={number}
```
获取全局图谱数据，用于前端可视化。

### GraphRAG上下文
```
GET /api/v1/graphrag/{kg_id}/context
```
获取实体的一度关联知识，转化为自然语言描述。

## 数据流程

```
非结构化文本 
    ↓
实体抽取 + 实体链接 (extractEntities.py)
    ↓
结构化JSON (data/output/)
    ↓
导入Neo4j (import_to_neo4j.py)
    ↓
知识图谱
    ↓
API查询 + GraphRAG (api.py)
```

## 示例

项目包含示例数据 `turing_raw_data_zhcn.txt`（艾伦·图灵的中文百科），可用于测试完整流程：

```bash
# 1. 抽取实体
python src/extractEntities.py

# 2. 导入数据库
python src/import_to_neo4j.py

# 3. 启动服务
python src/api.py

# 4. 访问API文档
# 浏览器打开 http://127.0.0.1:8000/docs
```

## 特性

- **GraphRAG支持**：将知识图谱转化为自然语言上下文
- **实体对齐**：通过Wikidata实现跨源实体对齐
- **并发优化**：使用线程池并发处理实体链接
- **增量更新**：支持Upsert语义，避免重复数据
- **自动文档**：FastAPI自动生成交互式API文档
