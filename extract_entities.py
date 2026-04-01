import spacy
import json
import os

# 1. 加载模型
nlp = spacy.load("zh_core_web_sm")

def extract_entities_from_file(input_path, output_path):
    # 2. 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    # 3. 读取输入文件内容
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 4. 使用 spaCy 处理文本
    doc = nlp(text)

    extracted_entities = []

    # 5. 遍历识别出的实体并进行类型映射
    for ent in doc.ents:
        entity_type = ent.label_
        
        if entity_type in ["PERSON"]:
            mapped_type = "Person"
        elif entity_type in ["GPE", "LOC"]:
            mapped_type = "Location"
        elif entity_type in ["ORG"]:
            mapped_type = "Organization"
        elif entity_type in ["EVENT"]:
            mapped_type = "Event"
        else:
            mapped_type = "Other" 
            
        extracted_entities.append({
            "entity": ent.text,
            "type": mapped_type,
            "raw_label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })

    # 6. 将结果保存为 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        # ensure_ascii=False 保证中文字符不会被转义成 Unicode 编码
        # indent=4 让输出的 JSON 格式更易读
        json.dump(extracted_entities, f, ensure_ascii=False, indent=4)

    print(f"抽取完成！结果已保存至: {output_path}")
    print(f"共识别出 {len()} 个实体。")

# === 执行部分 ===
# 在这里设置你的输入和输出路径extracted_entities
input_file_path = "turing_raw_data_zhcn.txt"  # 你的输入txt文件
output_json_path = "extracted_entities.json" # 输出的json文件

# 调用函数
extract_entities_from_file(input_file_path, output_json_path)