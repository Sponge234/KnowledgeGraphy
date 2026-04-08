import spacy
import json
import os
import difflib

nlp = spacy.load("zh_core_web_sm")

def build_dynamic_canonical_map(extracted_strings):
    unique_entities = sorted(list(set(extracted_strings)), key=len, reverse=True)
    canonical_map = {}
    
    for entity in unique_entities:
        matched = False
        for canonical in set(canonical_map.values()):
            similarity = difflib.SequenceMatcher(None, entity.lower(), canonical.lower()).ratio()
            
            if entity.lower() in canonical.lower() or similarity > 0.65:
                canonical_map[entity] = canonical
                matched = True
                break
                
        if not matched:
            canonical_map[entity] = entity
            
    return canonical_map


def extract_entities_from_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = nlp(text)

    raw_entities =[]
    category_entity_strings = {"Person": [], "Location": [], "Organization": [], "Event": [], "Other":[]}

    for ent in doc.ents:
        entity_type = ent.label_
        
        if entity_type in ["PERSON"]:
            mapped_type = "Person"
        elif entity_type in["GPE", "LOC"]:
            mapped_type = "Location"
        elif entity_type in ["ORG"]:
            mapped_type = "Organization"
        elif entity_type in ["EVENT"]:
            mapped_type = "Event"
        else:
            mapped_type = "Other" 
            
        clean_text = ent.text.strip()
        raw_entities.append({
            "entity": clean_text,
            "type": mapped_type,
            "raw_label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })
        
        category_entity_strings[mapped_type].append(clean_text)

    global_canonical_map = {}
    for mapped_type, entity_list in category_entity_strings.items():
        if entity_list:
            type_map = build_dynamic_canonical_map(entity_list)
            global_canonical_map.update(type_map)

    for item in raw_entities:
        item["canonical_name"] = global_canonical_map.get(item["entity"], item["entity"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw_entities, f, ensure_ascii=False, indent=4)
        
    print(f" 提取与自动消歧完成，共提取 {len(raw_entities)} 个实体。")

if __name__ == "__main__":
    input_file_path = "turing_raw_data_zhcn.txt"
    output_json_path = "extracted_entities.json" 

    extract_entities_from_file(input_file_path, output_json_path)