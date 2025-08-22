"""WN18RR dataset processing functions."""

import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from beartype import beartype
from tqdm import tqdm


@beartype
def download_wn18rr(output_dir: Path) -> Path:
    """Download WN18RR dataset files from SimKGC repository.
    
    Args:
        output_dir: Directory where the raw data will be saved
        
    Returns:
        Path to the downloaded data directory
    """
    repo_url = "https://github.com/intfloat/SimKGC.git"
    temp_dir = "temp_SimKGC"
    
    try:
        # Clean up any existing temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print(f"Cloning {repo_url}...")
        result = subprocess.run(
            ["git", "clone", repo_url, temp_dir], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")
        
        # Run the download script
        script_path = Path(temp_dir) / "scripts" / "download_wikidata5m.sh"
        if not script_path.exists():
            raise FileNotFoundError(f"Download script not found: {script_path}")
        
        print("Downloading WN18RR dataset...")
        os.chmod(script_path, 0o755)
        
        result = subprocess.run(
            ["bash", "scripts/download_wikidata5m.sh"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Download script failed: {result.stderr}")
        
        # Move WN18RR data to output directory
        source_data_dir = Path(temp_dir) / "data" / "WN18RR"
        output_path = Path(output_dir)
        wn18rr_output = output_path / "WN18RR"
        
        if source_data_dir.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            if wn18rr_output.exists():
                print(f"WN18RR data already exists at {wn18rr_output}")
            else:
                shutil.copytree(source_data_dir, wn18rr_output)
                print(f"WN18RR data saved to {wn18rr_output}")
        else:
            raise FileNotFoundError(f"WN18RR data not found at {source_data_dir}")
        
        return wn18rr_output
        
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def _parse_tsv_lines(content: str) -> List[Tuple[str, ...]]:
    """Parse TSV content into tuples."""
    lines = content.strip().split('\n')
    return [tuple(line.split('\t')) for line in lines if line.strip()]


def _clean_wn18rr_entity_name(raw_name: str) -> str:
    """Clean WN18RR entity name by removing __ prefix and POS tags.
    
    Example: '__stool_NN_2' -> 'stool'
    """
    # Remove __ prefix like SimKGC does
    clean_name = raw_name.replace('__', '')
    # Remove POS tags (last 2 parts after splitting by _)
    return " ".join(clean_name.split("_")[:-2]).strip()


@beartype
def create_entity_id2name_wn18rr(definitions_file: Path) -> Dict[str, str]:
    """Create entity_id2name mapping from WN18RR wordnet definitions file.
    
    Args:
        definitions_file: Path to wordnet-mlj12-definitions.txt
        
    Returns:
        Dictionary mapping entity IDs to cleaned entity names
    """
    if not definitions_file.exists():
        raise FileNotFoundError(f"Definitions file not found: {definitions_file}")
    
    with open(definitions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    definition_tuples = _parse_tsv_lines(content)
    entity_id2name = {}
    
    for entity_id, raw_name, _ in tqdm(definition_tuples, desc="Creating entity_id2name"):
        entity_id2name[entity_id] = _clean_wn18rr_entity_name(raw_name)
    
    return entity_id2name


@beartype
def create_entity_id2description_wn18rr(definitions_file: Path) -> Dict[str, str]:
    """Create entity_id2description mapping from WN18RR wordnet definitions file.
    
    Args:
        definitions_file: Path to wordnet-mlj12-definitions.txt
        
    Returns:
        Dictionary mapping entity IDs to descriptions
    """
    if not definitions_file.exists():
        raise FileNotFoundError(f"Definitions file not found: {definitions_file}")
    
    with open(definitions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    definition_tuples = _parse_tsv_lines(content)
    entity_id2description = {}
    
    for entity_id, _, description in tqdm(definition_tuples, desc="Creating entity_id2description"):
        entity_id2description[entity_id] = description.strip()
    
    return entity_id2description


@beartype
def create_relation_id2name_wn18rr(relations_file: Path) -> Dict[str, str]:
    """Create relation_id2name mapping from WN18RR relations file.
    
    Args:
        relations_file: Path to relations.dict
        
    Returns:
        Dictionary mapping relation IDs to human-readable names
    """
    if not relations_file.exists():
        raise FileNotFoundError(f"Relations file not found: {relations_file}")
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    relation_tuples = _parse_tsv_lines(content)
    relation_id2name = {}
    
    for index, relation_id in relation_tuples:
        # Convert underscores to spaces for readability
        relation_name = relation_id.replace("_", " ").strip()
        relation_id2name[relation_id] = relation_name
    
    return relation_id2name


@beartype
def create_entity_ids_wn18rr(entity_id2name: Dict[str, str], entity_id2description: Dict[str, str]) -> List[str]:
    """Create list of all entity IDs from name and description mappings.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        
    Returns:
        Sorted list of all unique entity IDs
    """
    all_entity_ids = set(entity_id2name.keys()) | set(entity_id2description.keys())
    return sorted(all_entity_ids)


@beartype
def process_wn18rr_dataset(data_dir: str, output_dir: str) -> None:
    """Complete WN18RR dataset processing pipeline with SimKGC compatibility.
    
    Args:
        data_dir: Directory containing raw WN18RR files
        output_dir: Directory to save processed files
    """
    from ..processors import truncate_entity_descriptions, preprocess_triplet_data
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Loading WN18RR entity names...")
    entity_id2name = create_entity_id2name_wn18rr(Path(data_dir)/'wordnet-mlj12-definitions.txt')
    
    print("Loading WN18RR entity descriptions...")
    entity_id2description = create_entity_id2description_wn18rr(Path(data_dir)/'wordnet-mlj12-definitions.txt')

    print("Loading WN18RR relation names...")
    relation_id2name = create_relation_id2name_wn18rr(Path(data_dir)/'relations.dict')

    # Combine entity names and descriptions (prioritize descriptions)
    entity_descriptions = {}
    for entity_id in set(entity_id2name.keys()) | set(entity_id2description.keys()):
        desc = entity_id2description.get(entity_id, '')
        name = entity_id2name.get(entity_id, '')
        # Use description if available, otherwise use name
        entity_descriptions[entity_id] = desc if desc else name
    
    # Apply SimKGC-compatible truncation for WN18RR
    print("Truncating entity descriptions...")
    entity_descriptions = truncate_entity_descriptions(
        entity_descriptions,
        dataset='wn18rr',
        content_type='entity'  # Uses 50 words for WN18RR entities
    )
    
    print("Truncating relation descriptions...")
    relation_descriptions = truncate_entity_descriptions(
        relation_id2name,
        dataset='wn18rr', 
        content_type='relation'  # Uses 30 words for WN18RR relations
    )
    
    # Process each split
    for split in ['train', 'valid', 'test']:
        input_file = os.path.join(data_dir, f"{split}.txt")
        output_file = output_path / f"{split}_processed.txt"
        
        if os.path.exists(input_file):
            print(f"Processing {split} split...")
            preprocess_triplet_data(
                triplets_file=input_file,
                entity_descriptions=entity_descriptions,
                relation_descriptions=relation_descriptions,
                output_file=str(output_file),
                dataset='wn18rr'
            )
        else:
            print(f"Warning: {input_file} not found, skipping {split} split")
    
    # Save Names, Descriptions and Relation Name
    with open(output_path / "entity_id2name.json", 'w', encoding='utf-8') as f:
        json.dump(entity_id2name, f, ensure_ascii=False, indent=4)
        
    with open(output_path / "entity_id2description.json", 'w', encoding='utf-8') as f:
        json.dump(entity_id2description, f, ensure_ascii=False, indent=4)

    with open(output_path / "relation_id2name.json", 'w', encoding='utf-8') as f:
        json.dump(relation_id2name, f, ensure_ascii=False, indent=4)
        
    print(f"WN18RR processing complete. Files saved to {output_path}")
