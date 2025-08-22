"""FB15k-237 dataset processing utilities."""

import json
import os
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from ..processors import truncate_entity_descriptions


def download_fb15k237(output_dir: str) -> None:
    """Download FB15k-237 dataset files.
    
    Args:
        output_dir: Directory to save the downloaded files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    base_url = "https://raw.githubusercontent.com/intfloat/SimKGC/main/data/FB15k237"
    
    files_to_download = [
        "train.txt",
        "valid.txt", 
        "test.txt",
        "FB15k_mid2name.txt",
        "FB15k_mid2description.txt"
    ]
    
    # Additional FB15k files from SimKGC data
    
    print(f"Downloading FB15k-237 dataset to {output_path}")
    
    for filename in files_to_download:
        url = f"{base_url}/{filename}"
        file_path = output_path / filename
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, file_path)
    
    # Note: FB15k_mid2name.txt and FB15k_mid2description.txt need to be obtained separately
    # These are part of the original FB15k dataset and used by SimKGC
    print("\nNote: You'll need to obtain FB15k_mid2name.txt and FB15k_mid2description.txt")
    print("from the original FB15k dataset for entity descriptions.")


def load_fb15k_entity_descriptions(data_dir: str) -> Dict[str, str]:
    """Load FB15k entity descriptions.
    
    Args:
        data_dir: Directory containing FB15k files
        
    Returns:
        Dictionary mapping entity IDs to descriptions
    """
    descriptions = {}
    names = {}
    
    # Load entity names
    name_file = os.path.join(data_dir, "FB15k_mid2name.txt")
    if os.path.exists(name_file):
        with open(name_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    entity_id = parts[0]
                    name = parts[1]
                    names[entity_id] = name
    
    # Load entity descriptions 
    desc_file = os.path.join(data_dir, "FB15k_mid2description.txt")
    if os.path.exists(desc_file):
        with open(desc_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    entity_id = parts[0]
                    description = parts[1]
                    descriptions[entity_id] = description
    
    # Combine names and descriptions, prioritizing descriptions
    combined = {}
    for entity_id in set(names.keys()) | set(descriptions.keys()):
        desc = descriptions.get(entity_id, '')
        name = names.get(entity_id, '')
        
        # Use description if available, otherwise use name
        if desc:
            combined[entity_id] = desc
        elif name:
            combined[entity_id] = name
        else:
            combined[entity_id] = ''
            
    return combined


def load_fb15k237_relations(data_dir: str) -> Dict[str, str]:
    """Load FB15k-237 relation names.
    
    Args:
        data_dir: Directory containing the relations.dict file
        
    Returns:
        Dictionary mapping relation IDs to names
    """
    relations = {}
    relations_file = os.path.join(data_dir, "relations.dict")
    
    if os.path.exists(relations_file):
        with open(relations_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    rel_id = parts[0]
                    rel_name = parts[1]
                    # Clean up relation name (remove namespace prefix)
                    if rel_name.startswith('/'):
                        rel_name = rel_name[1:].replace('/', ' ')
                    relations[rel_id] = rel_name
    
    return relations

def load_fb15k_entity_names(data_dir: str) -> Dict[str, str]:
    """Load FB15k entity names.
    
    Args:
        data_dir: Directory containing FB15k files
        
    Returns:
        Dictionary mapping entity IDs to names
    """
    names = {}
    
    # Load entity names
    name_file = os.path.join(data_dir, "FB15k_mid2name.txt")
    if os.path.exists(name_file):
        with open(name_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    entity_id = parts[0]
                    name = parts[1]
                    names[entity_id] = name        
    return names

def preprocess_fb15k237_triplets(
    data_dir: str,
    output_dir: str,
    entity_desc_max_words: int = 50,
    relation_desc_max_words: int = 10
) -> None:
    """Preprocess FB15k-237 triplets with entity and relation descriptions.
    
    Args:
        data_dir: Directory containing FB15k-237 data files
        output_dir: Directory to save preprocessed files
        entity_desc_max_words: Maximum words for entity descriptions
        relation_desc_max_words: Maximum words for relation descriptions
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load entity descriptions and relation names
    print("Loading entity descriptions...")

    entity_names = load_fb15k_entity_names(data_dir)

    entity_descriptions = load_fb15k_entity_descriptions(data_dir)
    
    print("Loading relation names...")
    relation_names = load_fb15k237_relations(data_dir)
    
    # Truncate descriptions
    print("Truncating entity descriptions...")
    entity_descriptions = truncate_entity_descriptions(
        entity_descriptions, 
        max_words=entity_desc_max_words
    )
    
    print("Truncating relation descriptions...")
    relation_names = truncate_entity_descriptions(
        relation_names,
        max_words=relation_desc_max_words
    )
    
    # Process each split
    for split in ['train', 'valid', 'test']:
        input_file = os.path.join(data_dir, f"{split}.txt")
        output_file = output_path / f"{split}_processed.txt"
        
        if not os.path.exists(input_file):
            print(f"Warning: {input_file} not found, skipping {split} split")
            continue
            
        print(f"Processing {split} split...")
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    head, relation, tail = parts[:3]
                    
                    # Get descriptions/names
                    head_desc = entity_descriptions.get(head, '')
                    tail_desc = entity_descriptions.get(tail, '')
                    rel_desc = relation_names.get(relation, '')
                    
                    # Write processed triplet
                    outfile.write(f"{head}\t{relation}\t{tail}\t{head_desc}\t{rel_desc}\t{tail_desc}\n")
    
    # Save Names, Descriptions and Relation Name
    with open(output_path / "entity_id2name.json", 'w', encoding='utf-8') as f:
        json.dump(entity_names, f, ensure_ascii=False, indent=4)
        
    with open(output_path / "entity_id2description.json", 'w', encoding='utf-8') as f:
        json.dump(entity_descriptions, f, ensure_ascii=False, indent=4)

    with open(output_path / "relation_id2name.json", 'w', encoding='utf-8') as f:
        json.dump(relation_names, f, ensure_ascii=False, indent=4)
    print(f"Preprocessing complete. Files saved to {output_path}")


def process_fb15k237_dataset(data_dir: str, output_dir: str) -> None:
    """Complete FB15k-237 dataset processing pipeline.
    
    Args:
        data_dir: Directory containing raw FB15k-237 files
        output_dir: Directory to save processed files
    """
    print("Starting FB15k-237 dataset processing...")
    
    # Use SimKGC-compatible truncation limits for FB15k-237
    preprocess_fb15k237_triplets(
        data_dir=data_dir,
        output_dir=output_dir,
        entity_desc_max_words=50,  # SimKGC uses 50 for entities
        relation_desc_max_words=10  # SimKGC uses 10 for FB15k-237 relations
    )
    
    print("FB15k-237 processing complete!")
