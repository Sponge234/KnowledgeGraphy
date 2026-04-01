import spacy
import json
import os

nlp = spacy.load("zh_core_web_sm")

def extract_entities_from_file(input_path, output_path):

    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = nlp(text)

    extracted_entities = []

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
 
        json.dump(extracted_entities, f, ensure_ascii=False, indent=4)

    print(f"抽取完成！结果已保存至: {output_path}")
    print(f"共识别出 {len()} 个实体。")

input_file_path = "turing_raw_data_zhcn.txt"
output_json_path = "extracted_entities.json" 


extract_entities_from_file(input_file_path, output_json_path)