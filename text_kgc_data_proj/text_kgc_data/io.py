"""I/O utilities for loading and saving data files."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from beartype import beartype


@beartype
def load_json(file_path: Path) -> Dict[str, str]:
    """Load a JSON file safely.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary loaded from JSON file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@beartype
def save_json(data: Dict[str, str], file_path: Path) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path where to save the JSON file
    """
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@beartype
def load_text_file(file_path: Path) -> str:
    """Load a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Content of the text file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


@beartype
def save_text_file(content: str, file_path: Path) -> None:
    """Save content to a text file.
    
    Args:
        content: Text content to save
        file_path: Path where to save the text file
    """
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


@beartype
def save_entity_ids_list(entity_ids: List[str], file_path: Path) -> None:
    """Save a list of entity IDs to a text file.
    
    Args:
        entity_ids: List of entity IDs
        file_path: Path where to save the entity IDs file
    """
    content = '\n'.join(entity_ids)
    save_text_file(content, file_path)


@beartype
def ensure_directory_exists(directory_path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    directory_path.mkdir(parents=True, exist_ok=True)


@beartype
def load_standardized_kg(dataset_dir: str) -> Dict[str, Dict[str, str]]:
    """Load standardized knowledge graph data from a dataset directory.
    
    This function loads the three standard files produced by the toolkit:
    - entity_id2name.json: Entity ID to name mappings
    - entity_id2description.json: Entity ID to description mappings  
    - relation_id2name.json: Relation ID to name mappings
    
    Args:
        dataset_dir: Path to directory containing standardized dataset files
        
    Returns:
        Dictionary with keys 'entities', 'descriptions', 'relations' containing
        the loaded mappings
        
    Raises:
        FileNotFoundError: If any required files are missing
        
    Example:
        >>> kg_data = load_standardized_kg("data/standardised/wn18rr")
        >>> entities = kg_data['entities']  # entity_id -> name
        >>> descriptions = kg_data['descriptions']  # entity_id -> description
        >>> relations = kg_data['relations']  # relation_id -> name
    """
    dataset_path = Path(dataset_dir)
    
    # Define expected file paths
    entity_names_file = dataset_path / "entity_id2name.json"
    entity_descriptions_file = dataset_path / "entity_id2description.json"
    relation_names_file = dataset_path / "relation_id2name.json"
    
    # Check that all files exist
    missing_files = []
    for file_path, file_desc in [
        (entity_names_file, "entity_id2name.json"),
        (entity_descriptions_file, "entity_id2description.json"), 
        (relation_names_file, "relation_id2name.json")
    ]:
        if not file_path.exists():
            missing_files.append(file_desc)
    
    if missing_files:
        raise FileNotFoundError(
            f"Missing required files in {dataset_path}: {', '.join(missing_files)}"
        )
    
    # Load all files
    return {
        'entities': load_json(entity_names_file),
        'descriptions': load_json(entity_descriptions_file),
        'relations': load_json(relation_names_file)
    }
