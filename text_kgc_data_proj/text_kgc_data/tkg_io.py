import json
from typing import Dict
from beartype import beartype
from text_kgc_data.models import TextualKG
    
@beartype
def load_tkg_from_files(
    entity_id2name_source_path: str= "entity_id2name.json",
    entity_id2description_source_path: str= "entity_id2description.json",
    relation_id2name_source_path: str= "relation_id2name.json"
) -> TextualKG:
    '''Load all text data from the knowledge graph.'''
    def load_json_file(file_path: str) -> Dict[str, str]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    
    entity_id2name = load_json_file(entity_id2name_source_path)
    entity_id2description = load_json_file(entity_id2description_source_path)
    relation_id2name = load_json_file(relation_id2name_source_path)
    
    return TextualKG(
        entity_id2name=entity_id2name,
        entity_id2description=entity_id2description,
        relation_id2name=relation_id2name
    )
    
@beartype
def load_tkg_from_folder(folder_path: str) -> TextualKG:
    '''Load all text data from the knowledge graph from a folder.'''
    entity_id2name_source_path = f"{folder_path}/entity_id2name.json"
    entity_id2description_source_path = f"{folder_path}/entity_id2description.json"
    relation_id2name_source_path = f"{folder_path}/relation_id2name.json"
    
    return load_tkg_from_files(
        entity_id2name_source_path,
        entity_id2description_source_path,
        relation_id2name_source_path
    )
    
@beartype
def save_tkg_to_files(
    tkg: TextualKG,
    entity_id2name_save_path: str = "entity_id2name.json",
    entity_id2description_save_path: str = "entity_id2description.json",
    relation_id2name_save_path: str = "relation_id2name.json"
):
    '''Save all text data from the knowledge graph to files.'''
    def save_json_file(data: Dict[str, str], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    save_json_file(tkg.entity_id2name, entity_id2name_save_path)
    save_json_file(tkg.entity_id2description, entity_id2description_save_path)
    save_json_file(tkg.relation_id2name, relation_id2name_save_path)
    
@beartype
def save_tkg_to_folder(
    tkg: TextualKG,
    folder_path: str,
) -> None:
    '''Save all text data from the knowledge graph to a folder.'''
    entity_id2name_save_path = f"{folder_path}/{entity_id2name_save_path}"
    entity_id2description_save_path = f"{folder_path}/{entity_id2description_save_path}"
    relation_id2name_save_path = f"{folder_path}/{relation_id2name_save_path}"
    
    save_tkg_to_files(
        entity_id2name_save_path,
        entity_id2description_save_path,
        relation_id2name_save_path,
        tkg
    )