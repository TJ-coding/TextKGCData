"""Wikidata5M dataset processing functions."""

import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
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
    """Python implementation of the provided bash script to download Wikidata5M dataset."""
    import urllib.request
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Download files
    files_to_download = {
        "wikidata5m_text.txt.gz": "https://huggingface.co/datasets/intfloat/wikidata5m/resolve/main/wikidata5m_text.txt.gz",
        "wikidata5m_transductive.tar.gz": "https://huggingface.co/datasets/intfloat/wikidata5m/resolve/main/wikidata5m_transductive.tar.gz",
        "wikidata5m_inductive.tar.gz": "https://huggingface.co/datasets/intfloat/wikidata5m/resolve/main/wikidata5m_inductive.tar.gz",
        "wikidata5m_alias.tar.gz": "https://huggingface.co/datasets/intfloat/wikidata5m/resolve/main/wikidata5m_alias.tar.gz",
    }
    for fname, url in files_to_download.items():
        dest = base_dir / fname
        if not dest.exists():
            print(f"Downloading {fname}...")
            urllib.request.urlretrieve(url, dest)
        else:
            print(f"{fname} already exists, skipping download.")

    # Extract tar files
    for tarfile in ["wikidata5m_transductive.tar.gz", "wikidata5m_inductive.tar.gz", "wikidata5m_alias.tar.gz"]:
        tar_path = base_dir / tarfile
        print(f"Extracting {tarfile}...")
        subprocess.run(["tar", "xvfz", str(tar_path)], cwd=base_dir, check=True)

    # Gunzip text file
    gz_path = base_dir / "wikidata5m_text.txt.gz"
    print("Unzipping wikidata5m_text.txt.gz...")
    subprocess.run(["gunzip", "-k", str(gz_path)], cwd=base_dir, check=True)

    # Create symlinks for transductive
    trans_dir = base_dir.parent / "wiki5m_trans"
    trans_dir.mkdir(parents=True, exist_ok=True)
    symlinks_trans = {
        "wikidata5m_relation.txt": trans_dir / "wikidata5m_relation.txt",
        "wikidata5m_text.txt": trans_dir / "wikidata5m_text.txt",
        "wikidata5m_entity.txt": trans_dir / "wikidata5m_entity.txt",
        "wikidata5m_transductive_train.txt": trans_dir / "train.txt",
        "wikidata5m_transductive_valid.txt": trans_dir / "valid.txt",
        "wikidata5m_transductive_test.txt": trans_dir / "test.txt",
    }
    for src_name, dest_path in symlinks_trans.items():
        src_path = base_dir / src_name
        if not dest_path.exists():
            print(f"Creating symlink: {dest_path} -> {src_path}")
            dest_path.symlink_to(src_path)
        else:
            print(f"Symlink {dest_path} already exists.")

    # Create symlinks for inductive
    ind_dir = base_dir.parent / "wiki5m_ind"
    ind_dir.mkdir(parents=True, exist_ok=True)
    symlinks_ind = {
        "wikidata5m_relation.txt": ind_dir / "wikidata5m_relation.txt",
        "wikidata5m_text.txt": ind_dir / "wikidata5m_text.txt",
        "wikidata5m_entity.txt": ind_dir / "wikidata5m_entity.txt",
        "wikidata5m_inductive_train.txt": ind_dir / "train.txt",
        "wikidata5m_inductive_valid.txt": ind_dir / "valid.txt",
        "wikidata5m_inductive_test.txt": ind_dir / "test.txt",
    }
    for src_name, dest_path in symlinks_ind.items():
        src_path = base_dir / src_name
        if not dest_path.exists():
            print(f"Creating symlink: {dest_path} -> {src_path}")
            dest_path.symlink_to(src_path)
        else:
            print(f"Symlink {dest_path} already exists.")

    print("Done")
    return base_dir


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
        entity_id, entity_name = _extract_first_value(parts)
        entity_id2name[entity_id] = entity_name
     
    
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
        relation_id, relation_name = _extract_first_value(parts)
        relation_id2name[relation_id] = relation_name

    
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


@beartype
def download_wikidata5m_transductive(output_dir: str) -> None:
    """Download Wikidata5M transductive variant.
    
    Args:
        output_dir: Directory to save the downloaded files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Base URL for Wikidata5M files
    base_url = "https://www.dropbox.com/s"
    
    # Transductive split files
    transductive_files = {
        "wikidata5m_transductive_train.txt": "563omb2a0lnkrbl/wikidata5m_transductive_train.txt",
        "wikidata5m_transductive_valid.txt": "5ff3seg5kczz60n/wikidata5m_transductive_valid.txt", 
        "wikidata5m_transductive_test.txt": "hl42h6objbx71sy/wikidata5m_transductive_test.txt"
    }
    
    # Common files
    common_files = {
        "wikidata5m_entity.txt": "563omb2a0lnkrbl/wikidata5m_entity.txt",
        "wikidata5m_relation.txt": "jdl80cxy3tpk8xw/wikidata5m_relation.txt",
        "wikidata5m_text.txt": "7jp4ib8zo3i6y2k/wikidata5m_text.txt"
    }
    
    all_files = {**transductive_files, **common_files}
    
    print(f"Downloading Wikidata5M transductive dataset to {output_path}")
    
    for filename, url_path in all_files.items():
        file_path = output_path / filename
        if not file_path.exists():
            url = f"{base_url}/{url_path}?dl=1"
            print(f"Downloading {filename}...")
            import urllib.request
            urllib.request.urlretrieve(url, file_path)
        else:
            print(f"{filename} already exists, skipping")


@beartype 
def download_wikidata5m_inductive(output_dir: str) -> None:
    """Download Wikidata5M inductive variant.
    
    Args:
        output_dir: Directory to save the downloaded files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Base URL for Wikidata5M files
    base_url = "https://www.dropbox.com/s"
    
    # Inductive split files
    inductive_files = {
        "wikidata5m_inductive_train.txt": "563omb2a0lnkrbl/wikidata5m_inductive_train.txt",
        "wikidata5m_inductive_valid.txt": "5ff3seg5kczz60n/wikidata5m_inductive_valid.txt",
        "wikidata5m_inductive_test.txt": "hl42h6objbx71sy/wikidata5m_inductive_test.txt"
    }
    
    # Common files
    common_files = {
        "wikidata5m_entity.txt": "563omb2a0lnkrbl/wikidata5m_entity.txt",
        "wikidata5m_relation.txt": "jdl80cxy3tpk8xw/wikidata5m_relation.txt", 
        "wikidata5m_text.txt": "7jp4ib8zo3i6y2k/wikidata5m_text.txt"
    }
    
    all_files = {**inductive_files, **common_files}
    
    print(f"Downloading Wikidata5M inductive dataset to {output_path}")
    
    for filename, url_path in all_files.items():
        file_path = output_path / filename
        if not file_path.exists():
            url = f"{base_url}/{url_path}?dl=1"
            print(f"Downloading {filename}...")
            import urllib.request
            urllib.request.urlretrieve(url, file_path)
        else:
            print(f"{filename} already exists, skipping")


@beartype
def preprocess_wikidata5m_variant(
    data_dir: str,
    variant: str = "transductive",
    entity_desc_max_words: int = 50,
    relation_desc_max_words: int = 30
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """Preprocess Wikidata5M transductive or inductive variant.
    
    Args:
        data_dir: Directory containing raw Wikidata5M files
        output_dir: Directory to save processed files
        variant: Either "transductive" or "inductive"
        entity_desc_max_words: Maximum words for entity descriptions
        relation_desc_max_words: Maximum words for relation descriptions
    """
    from ..processors import truncate_entity_descriptions
    
    if variant not in ["transductive", "inductive"]:
        raise ValueError("variant must be 'transductive' or 'inductive'")
    
    # Load entity and relation mappings
    print("Loading entity names and descriptions...")
    entity_id2name = create_entity_id2name_wikidata5m(Path(data_dir)/'wikidata5m_entity.txt')
    entity_id2description = create_entity_id2description_wikidata5m(Path(data_dir)/'wikidata5m_text.txt')

    print("Loading relation names...")
    relation_id2name = create_relation_id2name_wikidata5m(Path(data_dir)/'wikidata5m_relation.txt')

    # Fill missing entries (if needed, can add a fill_missing_entity_entries step)
    # Combine entity names and descriptions (prioritize descriptions)
    entity_descriptions = {}
    for entity_id in set(entity_id2name.keys()) | set(entity_id2description.keys()):
        desc = entity_id2description.get(entity_id, '')
        name = entity_id2name.get(entity_id, '')
        entity_descriptions[entity_id] = desc if desc else name

    # Truncate descriptions
    print("Truncating entity descriptions...")
    from ..processors import truncate_entity_descriptions
    truncated_entity_descriptions = truncate_entity_descriptions(
        entity_descriptions,
        max_words=entity_desc_max_words,
        dataset='wikidata5m',
        content_type='entity'
    )

    print("Truncating relation descriptions...")
    truncated_relation_descriptions = truncate_entity_descriptions(
        relation_id2name,
        max_words=relation_desc_max_words,
        dataset='wikidata5m',
        content_type='relation'
    )
       
    print(f"Wikidata5M {variant} preprocessing complete.")
    return  entity_id2name,  truncated_entity_descriptions,  truncated_relation_descriptions,

def preprocess_wikidata5m_transductive(data_dir: str, entity_desc_max_words: int = 50, relation_desc_max_words: int = 30):
    """Preprocess Wikidata5M transductive variant and return processed dicts and splits."""
    return preprocess_wikidata5m_variant(
        data_dir=data_dir,
        variant="transductive",
        entity_desc_max_words=entity_desc_max_words,
        relation_desc_max_words=relation_desc_max_words
    )

def preprocess_wikidata5m_inductive(data_dir: str, entity_desc_max_words: int = 50, relation_desc_max_words: int = 30):
    """Preprocess Wikidata5M inductive variant and return processed dicts and splits."""
    return preprocess_wikidata5m_variant(
        data_dir=data_dir,
        variant="inductive",
        entity_desc_max_words=entity_desc_max_words,
        relation_desc_max_words=relation_desc_max_words
    )


@beartype
def process_wikidata5m_transductive(data_dir: str, output_dir: str) -> None:
    """Process Wikidata5M transductive dataset with SimKGC-compatible settings.
    
    Args:
        data_dir: Directory containing raw files
        output_dir: Directory to save processed files
    """
    preprocess_wikidata5m_variant(
        data_dir=data_dir,
        output_dir=output_dir,
        variant="transductive",
        entity_desc_max_words=50,  # SimKGC default for entities
        relation_desc_max_words=30  # SimKGC default for Wikidata5M relations
    )


@beartype
def process_wikidata5m_inductive(data_dir: str, output_dir: str) -> None:
    """Process Wikidata5M inductive dataset with SimKGC-compatible settings.
    
    Args:
        data_dir: Directory containing raw files
        output_dir: Directory to save processed files
    """
    preprocess_wikidata5m_variant(
        data_dir=data_dir,
        output_dir=output_dir,
        variant="inductive",
        entity_desc_max_words=50,  # SimKGC default for entities
        relation_desc_max_words=30  # SimKGC default for Wikidata5M relations
    )