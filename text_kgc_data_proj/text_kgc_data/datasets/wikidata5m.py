"""Wikidata5M dataset processing functions."""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from beartype import beartype
from tqdm import tqdm


@beartype
def download_wikidata5m(output_dir: Path) -> Path:
    """Download Wikidata5M dataset files from SimKGC repository.
    
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
        
        print("Downloading Wikidata5M dataset...")
        os.chmod(script_path, 0o755)
        
        result = subprocess.run(
            ["bash", "scripts/download_wikidata5m.sh"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Download script failed: {result.stderr}")
        
        # Move Wikidata5M data to output directory
        source_data_dir = Path(temp_dir) / "data" / "wikidata5m"
        output_path = Path(output_dir)
        wikidata5m_output = output_path / "wikidata5m"
        
        if source_data_dir.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            if wikidata5m_output.exists():
                print(f"Wikidata5M data already exists at {wikidata5m_output}")
            else:
                shutil.copytree(source_data_dir, wikidata5m_output)
                print(f"Wikidata5M data saved to {wikidata5m_output}")
        else:
            raise FileNotFoundError(f"Wikidata5M data not found at {source_data_dir}")
        
        return wikidata5m_output
        
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def _parse_tsv_lines(content: str) -> List[Tuple[str, ...]]:
    """Parse TSV content into tuples."""
    lines = content.strip().split('\n')
    return [tuple(line.split('\t')) for line in lines if line.strip()]


def _extract_first_value(tsv_parts: Tuple[str, ...]) -> Tuple[str, str]:
    """Extract ID and first value from TSV parts.
    
    Wikidata5M files contain multiple alternative names/descriptions.
    We take the first one for consistency.
    """
    if len(tsv_parts) < 2:
        raise ValueError(f"Expected at least 2 parts, got {len(tsv_parts)}: {tsv_parts}")
    
    entity_id = tsv_parts[0]
    first_value = tsv_parts[1].strip()
    return entity_id, first_value


@beartype
def create_entity_id2name_wikidata5m(entity_names_file: Path) -> Dict[str, str]:
    """Create entity_id2name mapping from Wikidata5M entity names file.
    
    Args:
        entity_names_file: Path to wikidata5m_entity.txt
        
    Returns:
        Dictionary mapping entity IDs to entity names (first name if multiple)
    """
    if not entity_names_file.exists():
        raise FileNotFoundError(f"Entity names file not found: {entity_names_file}")
    
    with open(entity_names_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entity_name_tuples = _parse_tsv_lines(content)
    entity_id2name = {}
    
    for parts in tqdm(entity_name_tuples, desc="Creating entity_id2name"):
        try:
            entity_id, entity_name = _extract_first_value(parts)
            entity_id2name[entity_id] = entity_name
        except ValueError as e:
            print(f"Warning: Skipping malformed line: {e}")
            continue
    
    return entity_id2name


@beartype
def create_entity_id2description_wikidata5m(entity_descriptions_file: Path) -> Dict[str, str]:
    """Create entity_id2description mapping from Wikidata5M descriptions file.
    
    Args:
        entity_descriptions_file: Path to wikidata5m_text.txt
        
    Returns:
        Dictionary mapping entity IDs to descriptions (first description if multiple)
    """
    if not entity_descriptions_file.exists():
        raise FileNotFoundError(f"Entity descriptions file not found: {entity_descriptions_file}")
    
    with open(entity_descriptions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entity_desc_tuples = _parse_tsv_lines(content)
    entity_id2description = {}
    
    for parts in tqdm(entity_desc_tuples, desc="Creating entity_id2description"):
        try:
            entity_id, description = _extract_first_value(parts)
            entity_id2description[entity_id] = description
        except ValueError as e:
            print(f"Warning: Skipping malformed line: {e}")
            continue
    
    return entity_id2description


@beartype
def create_relation_id2name_wikidata5m(relations_file: Path) -> Dict[str, str]:
    """Create relation_id2name mapping from Wikidata5M relations file.
    
    Args:
        relations_file: Path to wikidata5m_relation.txt
        
    Returns:
        Dictionary mapping relation IDs to relation names (first name if multiple)
    """
    if not relations_file.exists():
        raise FileNotFoundError(f"Relations file not found: {relations_file}")
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    relation_tuples = _parse_tsv_lines(content)
    relation_id2name = {}
    
    for parts in tqdm(relation_tuples, desc="Creating relation_id2name"):
        try:
            relation_id, relation_name = _extract_first_value(parts)
            relation_id2name[relation_id] = relation_name
        except ValueError as e:
            print(f"Warning: Skipping malformed line: {e}")
            continue
    
    return relation_id2name


@beartype
def create_entity_ids_wikidata5m(entity_id2name: Dict[str, str], entity_id2description: Dict[str, str]) -> List[str]:
    """Create list of all entity IDs from name and description mappings.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        
    Returns:
        Sorted list of all unique entity IDs
    """
    all_entity_ids = set(entity_id2name.keys()) | set(entity_id2description.keys())
    return sorted(all_entity_ids)
