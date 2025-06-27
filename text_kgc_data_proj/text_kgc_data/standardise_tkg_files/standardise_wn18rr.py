from typing import Dict, List, Tuple
from beartype import beartype
import json
from text_kgc_data.helpers import text_to_tsvs
from tqdm import tqdm

"""Preprocess WN18RR into loadable format """

@beartype
def create_word_ids_and_words_and_definitions(
    definiton_triplets: List[Tuple[str, str, str]],
) -> Tuple[List[str], List[str], List[str]]:
    word_ids, words, definitions = zip(*definiton_triplets)
    words = [
        " ".join(triplet[1].split("_")[:-2]).strip() for triplet in tqdm(definiton_triplets, desc="Processing words", total=len(definiton_triplets))
    ]
    return list(word_ids), words, list(definitions)


@beartype
def standardize_wn18rr_entity_files(
    definitions_source_path: str = "WN18RR/wordnet-mlj12-definitions.txt",
    entity_id_save_path: str = "wn18rr_tkg/entity_ids.txt",
    entity_id2name_save_path: str = "wn18rr_tkg/entity_id2_name.json",
    entity_id2description_save_path: str = "wn18rr_tkg/entity_id2_description.json",
):
    """Ceate a mapping of entity ids to their descriptions"""


    with open(definitions_source_path, "r") as handle:
        entity_definitions_text = handle.read()
        
    entity_dictionary_tsv: List[Tuple[str, ...]] = text_to_tsvs(entity_definitions_text)
    entity_ids, entity_names, definitions = create_word_ids_and_words_and_definitions(
        entity_dictionary_tsv
    )
    
    with open(entity_id_save_path, "w") as handle:
        handle.write("\n".join(entity_ids))

    entity_id2name: Dict[str, str] = dict(zip(entity_ids, entity_names))
    with open(entity_id2name_save_path, "w") as handle:
        json.dump(entity_id2name, handle, indent=4)
    
    word_ids2description = dict(zip(entity_ids, definitions))
    with open(entity_id2description_save_path, "w") as handle:
        json.dump(word_ids2description, handle, indent=4)

@beartype
def standardize_wn18rr_relation_file(
    relations_source_path: str = "WN18RR/relations.dict",
    relation_id2name_save_path: str = "wn18rr_tkg/wn18rr-relations2description.json",
):
    """Ceate a mapping of relation ids to their descriptions"""

    with open(relations_source_path, "r") as handle:
        relation_text = handle.read()
    lines: List[str] = relation_text.strip().split("\n")
    tuples: List[Tuple[str, str]] = [
        tuple([i.strip() for i in line.split("\t")]) for line in lines
    ]
    index, relation_ids = zip(*tuples)
    relation_descriptions: List[str] = [
        relation_id.replace("_", " ").strip() for relation_id in relation_ids
    ]
    relation_id2description = dict(zip(relation_ids, relation_descriptions))
    with open(relation_id2name_save_path, "w") as handle:
        json.dump(relation_id2description, handle)


