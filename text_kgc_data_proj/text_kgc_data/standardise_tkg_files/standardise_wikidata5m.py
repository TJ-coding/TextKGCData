from typing import Dict, List, Optional, Tuple
from beartype import beartype
import json

from tqdm import tqdm
from text_kgc_data.helpers import text_to_tsvs

def tsvs_to_dict(tsvs: List[List[str]], file_name: Optional[str]=None)->Dict[str, str]:
    '''Wikidata5m gives multiple candidate names, we pick the first one.
    E.g. "Q42\tObama\tBarak Obama\tBarack Hussein Obama\tBarack Hussein Obama Sr.\tBarack Hussein Obama Jr.\tBarack Hussein Obama III"
    '''
    id2value: Dict[str, str] = {}
    for i, tsv in enumerate(tqdm(tsvs, desc= f'Loading {file_name}', total=len(tsvs) if file_name != None else None)):
        if len(tsv) < 2:
            print(f"Error line in {file_name}: {tsv}")
            raise ValueError(f"{i}th tsv: Expected at least 2 parts in line, got {len(tsv)}: {tsv}")
        id2value[tsv[0]] = tsv[1]
    return id2value

@beartype
def standardize_wikidata5m_entity_files(
    entity_names_source_path: str = "wikidata5m/wikidata5m_entity.txt",
    entity_descriptions_source_path: str = "wikidata5m/wikidata5m_text.txt",
    entity_id_save_path: str = "wikidata5m_tkg/entity_ids.txt",
    entity_id2name_save_path: str = "wikidata5m_tkg/entity_id2_name.json",
    entity_id2description_save_path: str = "wikidata5m_tkg/entity_id2_description.json",
):
    '''Creates entity_id2name.json, entity_id2description.json and entity_ids.txt from the raw wikidata5m files.
    The first name is picked as the entity name.
    '''

    with open(entity_names_source_path, "r") as handle:
        entity_names_text: str = handle.read()
    
    entity_names_tsvs: List[Tuple[str, ...]] = text_to_tsvs(entity_names_text)
    entity_id2name: Dict[str, str] =  tsvs_to_dict(entity_names_tsvs, file_name=entity_names_source_path)
    
    with open(entity_descriptions_source_path, "r") as handle:
        entity_descriptions_text: str = handle.read()   
    entity_descriptions_tsvs: List[Tuple[str, ...]] = text_to_tsvs(entity_descriptions_text)
    entity_id2description: Dict[str, str] = tsvs_to_dict(entity_descriptions_tsvs, file_name=entity_descriptions_source_path)

    entity_ids: List[str] = list(set(entity_id2name.keys()).union(set(entity_id2description.keys())))

    with open(entity_id_save_path, "w") as handle:
        handle.write("\n".join(entity_ids))

    with open(entity_id2name_save_path, "w") as handle:
        json.dump(entity_id2name, handle, indent=4)  
        
    with open(entity_id2description_save_path, "w") as handle:
        json.dump(entity_id2description, handle, indent=4)

@beartype
def standardize_wikidata5m_relation_file(
    relations_source_path: str = "wikidata5m/wikidata5m_relation.txt",
    relation_id2name_save_path: str = "wikidata5m_tkg/relation_id2name.json",
):
    """Ceate relation_id2name.json from wikidata5m relations file.
    The first name is picked as the relation name."""

    with open(relations_source_path, "r") as handle:
        relation_text = handle.read()
    
    telation_tsvs: List[Tuple, str] = text_to_tsvs(relation_text)
    relation_id2name: Dict[str, str] = tsvs_to_dict(telation_tsvs, file_name=relations_source_path)
    
    with open(relation_id2name_save_path, "w") as handle:
        json.dump(relation_id2name, handle, indent=4)