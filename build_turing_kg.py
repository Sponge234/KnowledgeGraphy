from SPARQLWrapper import SPARQLWrapper, JSON
from neo4j import GraphDatabase

# ==========================================
# 1. 配置 Neo4j 连接
# ==========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "qwer1234" # 替换为你的密码

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ==========================================
# 2. 从 DBpedia 获取数据 (获取简介和知名成就)
# ==========================================
def get_dbpedia_data():
    print("正在从 DBpedia 获取数据...")
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    
    # SPARQL 查询：获取英文简介和 knownFor 的实体名字
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?abstract ?knownForLabel WHERE {
      dbr:Alan_Turing dbo:abstract ?abstract .
      OPTIONAL { 
          dbr:Alan_Turing dbo:knownFor ?known .
          ?known rdfs:label ?knownForLabel .
          FILTER (lang(?knownForLabel) = 'en')
      }
      FILTER (lang(?abstract) = 'en')
    } LIMIT 10
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # 解析结果
    abstract = results["results"]["bindings"][0]["abstract"]["value"]
    known_for_list = [
        item["knownForLabel"]["value"] 
        for item in results["results"]["bindings"] 
        if "knownForLabel" in item
    ]
    return abstract, known_for_list

# ==========================================
# 3. 从 Wikidata 获取数据 (获取母校和导师)
# ==========================================
def get_wikidata_data():
    print("正在从 Wikidata 获取数据...")
    # 注意：Wikidata 要求设置 User-Agent，否则可能会被拦截
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", 
                           agent="TuringKGBot/1.0 (someone@example.com) SPARQLWrapper/1.8")
    
    # SPARQL 查询：P69(母校), P184(博士导师)
    query = """
    SELECT ?schoolLabel ?advisorLabel WHERE {
      wd:Q7251 wdt:P69 ?school .
      wd:Q7251 wdt:P184 ?advisor .
      
      # 获取英文标签
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    } LIMIT 10
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    schools = set()
    advisors = set()
    for item in results["results"]["bindings"]:
        if "schoolLabel" in item:
            schools.add(item["schoolLabel"]["value"])
        if "advisorLabel" in item:
            advisors.add(item["advisorLabel"]["value"])
            
    return list(schools), list(advisors)

# ==========================================
# 4. 将数据写入 Neo4j (融合构建图谱)
# ==========================================
def build_knowledge_graph():
    # 抓取数据
    abstract, known_for = get_dbpedia_data()
    schools, advisors = get_wikidata_data()
    
    print("数据抓取完毕，正在写入 Neo4j...")
    
    with driver.session() as session:
        # 4.1 创建图灵核心节点并写入 DBpedia 的简介 (Merge确保不重复创建)
        session.run("""
            MERGE (t:Person {name: "Alan Turing"})
            SET t.wikidata_id = 'Q7251',
                t.dbpedia_id = 'Alan_Turing',
                t.abstract = $abstract
        """, abstract=abstract)
        
        # 4.2 写入成就 (来自 DBpedia)
        for concept in known_for:
            session.run("""
                MATCH (t:Person {name: "Alan Turing"})
                MERGE (c:Concept {name: $concept})
                MERGE (t)-[:KNOWN_FOR]->(c)
            """, concept=concept)
            
        # 4.3 写入母校 (来自 Wikidata)
        for school in schools:
            session.run("""
                MATCH (t:Person {name: "Alan Turing"})
                MERGE (u:University {name: $school})
                MERGE (t)-[:EDUCATED_AT]->(u)
            """, school=school)
            
        # 4.4 写入博士导师 (来自 Wikidata)
        for advisor in advisors:
            session.run("""
                MATCH (t:Person {name: "Alan Turing"})
                MERGE (a:Person {name: $advisor})
                MERGE (t)-[:DOCTORAL_ADVISOR]->(a)
            """, advisor=advisor)

    print("✅ 知识图谱构建完成！请打开 Neo4j Browser 查看。")

if __name__ == "__main__":
    build_knowledge_graph()
    driver.close()