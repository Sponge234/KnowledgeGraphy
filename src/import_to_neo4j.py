import os
import json
from neo4j import GraphDatabase

# ==========================================
# 配置区
# ==========================================
# Neo4j 数据库连接信息
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j_kg" 

# 存放生成的 JSON 数据的文件夹（从这里读取）
OUTPUT_FOLDER = "grapth_build\data\output"

# ==========================================
# 存储逻辑区
# ==========================================
class Neo4jStorage:
    def __init__(self, uri, user, pwd):
        # 创建数据库驱动实例
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def upsert_knowledge_graph(self, kg_data: dict):
        if not kg_data: return
        # 开启一个会话
        # 先写入所有节点（实体）
        # 再写入所有边（关系）
        with self.driver.session() as session:
            if kg_data.get('entities'):
                session.execute_write(self._upsert_nodes, kg_data['entities'])
            if kg_data.get('relations'):
                session.execute_write(self._upsert_edges_apoc, kg_data['relations'])

    @staticmethod
    def _upsert_nodes(tx, nodes: list):
        # 使用 Entity 作为基础标签进行 MERGE
        # 存入基本属性
        # WITH 传递变量后，调用 APOC 根据 node.type 动态添加具体的分类标签
        query = """
        UNWIND $nodes AS node
        MERGE (n:Entity {kg_id: node.kg_id})
        ON CREATE SET n.name = node.name, 
                      n.type = node.type, 
                      n.description = node.description, 
                      n.aliases = [node.name]
        ON MATCH SET n.aliases = CASE WHEN NOT node.name IN coalesce(n.aliases,[]) THEN coalesce(n.aliases,[]) + node.name ELSE n.aliases END
        WITH n, node
        // 过滤掉 type 为空的情况，将节点类型字符串转换为标签添加上去
        CALL apoc.do.when(
            node.type IS NOT NULL AND node.type <> '',
            'CALL apoc.create.addLabels(n, [type]) YIELD node RETURN node',
            'RETURN n AS node',
            {n: n, type: node.type}
        ) YIELD value
        RETURN count(n)
        """
        tx.run(query, nodes=nodes)

    @staticmethod
    def _upsert_edges_apoc(tx, edges: list):
        # UNWIND: 批量处理关系列表
        # MATCH: 分别找到起点和终点节点（根据之前生成的 kg_id）
        # toUpper/replace: 将关系类型统一格式化（如 "born in" 变为 "BORN_IN"）
        # apoc.merge.relationship: 动态创建/匹配关系
        query = """
        UNWIND $edges AS edge
        MATCH (source:Entity {kg_id: edge.source_kg_id})
        MATCH (target:Entity {kg_id: edge.target_kg_id})
        WITH source, target, edge, toUpper(replace(edge.relation_type, ' ', '_')) AS relType
        CALL apoc.merge.relationship(source, relType, {}, {}, target, {}) YIELD rel
        RETURN count(rel)
        """
        tx.run(query, edges=edges)

# ==========================================
# 主入口
# ==========================================
if __name__ == "__main__":
    print("======  Neo4j 图数据库导入启动 ======")
    
    if not os.path.exists(OUTPUT_FOLDER):
        print(f"  找不到文件夹 {OUTPUT_FOLDER}，请先运行抽取脚本生成数据。")
        exit()
        
    json_files =[f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.json')]
    
    if not json_files:
        print(f"  在 {OUTPUT_FOLDER} 文件夹下未找到 .json 数据文件。")
    else:
        try:
            # 初始化 Neo4j 存储
            storage = Neo4jStorage(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
            
            for file_name in json_files:
                file_path = os.path.join(OUTPUT_FOLDER, file_name)
                print(f"\n 正在导入数据: {file_name}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)
                
                print(f"  [Import] 写入 Neo4j 节点与关系...")
                storage.upsert_knowledge_graph(kg_data)
                print(f" 文件 {file_name} 成功导入图数据库！")
                
            storage.driver.close()
            
        except Exception as e:
            print(f" 运行过程中发生错误: {e}")

    print("\n 所有数据导入完毕。")