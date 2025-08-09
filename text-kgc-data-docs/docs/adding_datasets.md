# Adding New Datasets

This guide explains how to add support for new knowledge graph datasets to the TextKGCData toolkit.

## Overview

The TextKGCData toolkit follows a functional architecture where each dataset has its own module containing specific processing functions. To add a new dataset, you'll need to:

1. Create a new dataset module
2. Implement the required functions
3. Add CLI commands
4. Update the main exports

## Creating a Dataset Module

Create a new file in `text_kgc_data/datasets/` named after your dataset (e.g., `my_dataset.py`).

### Required Functions

Each dataset module should implement these core functions:

```python
from pathlib import Path
from typing import Dict
from beartype import beartype

@beartype
def download_my_dataset(output_dir: Path) -> Path:
    """Download dataset files.
    
    Args:
        output_dir: Directory where raw data will be saved
        
    Returns:
        Path to the downloaded data directory
    """
    # Implementation here
    pass

@beartype
def create_entity_id2name_my_dataset(raw_data_dir: Path, output_file: Path) -> Dict[str, str]:
    """Create entity ID to name mapping.
    
    Args:
        raw_data_dir: Directory containing raw dataset files
        output_file: Where to save the mapping JSON file
        
    Returns:
        Dictionary mapping entity IDs to names
    """
    # Implementation here
    pass

@beartype
def create_entity_id2description_my_dataset(raw_data_dir: Path, output_file: Path) -> Dict[str, str]:
    """Create entity ID to description mapping.
    
    Args:
        raw_data_dir: Directory containing raw dataset files
        output_file: Where to save the mapping JSON file
        
    Returns:
        Dictionary mapping entity IDs to descriptions
    """
    # Implementation here
    pass

@beartype
def create_relation_id2name_my_dataset(raw_data_dir: Path, output_file: Path) -> Dict[str, str]:
    """Create relation ID to name mapping.
    
    Args:
        raw_data_dir: Directory containing raw dataset files
        output_file: Where to save the mapping JSON file
        
    Returns:
        Dictionary mapping relation IDs to names
    """
    # Implementation here
    pass
```

## Function Naming Convention

Functions should be named to clearly describe what they create:

- `create_entity_id2name_*` - Creates entity ID to name mappings
- `create_entity_id2description_*` - Creates entity ID to description mappings
- `create_relation_id2name_*` - Creates relation ID to name mappings
- `download_*` - Downloads raw dataset files

## Adding CLI Commands

Update `text_kgc_data/cli.py` to add your dataset commands:

```python
# Add imports
from text_kgc_data.datasets.my_dataset import (
    download_my_dataset,
    create_entity_id2name_my_dataset,
    create_entity_id2description_my_dataset,
    create_relation_id2name_my_dataset,
)

# Create subcommand app
my_dataset_app = typer.Typer(help="My Dataset processing commands")

@my_dataset_app.command("download")
@beartype
def download_my_dataset_cli(
    output_dir: Path = typer.Argument(..., help="Output directory for raw data"),
) -> None:
    """Download My Dataset files."""
    result_dir = download_my_dataset(output_dir)
    typer.echo(f"Downloaded My Dataset to: {result_dir}")

# Add more commands...

# Register with main app
app.add_typer(my_dataset_app, name="my-dataset")
```

## Updating Exports

Add your functions to `text_kgc_data/__init__.py`:

```python
# Add to imports
from text_kgc_data.datasets.my_dataset import (
    download_my_dataset,
    create_entity_id2name_my_dataset,
    create_entity_id2description_my_dataset,
    create_relation_id2name_my_dataset,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "download_my_dataset",
    "create_entity_id2name_my_dataset", 
    "create_entity_id2description_my_dataset",
    "create_relation_id2name_my_dataset",
]
```

## Testing Your Dataset

You can test your dataset functions both programmatically and via CLI:

```python
# Programmatic usage
from text_kgc_data import download_my_dataset, create_entity_id2name_my_dataset

data_dir = download_my_dataset(Path("./data"))
mappings = create_entity_id2name_my_dataset(data_dir, Path("./mappings.json"))
```

```bash
# CLI usage  
text-kgc my-dataset download ./data
text-kgc my-dataset create-entity-mappings ./data ./mappings.json
```

## Example: Existing Datasets

Look at `datasets/wn18rr.py` and `datasets/wikidata5m.py` for complete examples of dataset implementations following this pattern.