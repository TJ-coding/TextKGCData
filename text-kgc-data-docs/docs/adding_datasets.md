# Adding New Datasets - Developer Guide

This guide explains how to add support for new knowledge graph datasets to the `text-kgc-data` toolkit. Follow these steps to maintain consistency with the existing architecture and SimKGC compatibility.

---

## 📋 Prerequisites

Before adding a new dataset, ensure you have:

- Understanding of the dataset's structure and format
- Knowledge of any special preprocessing requirements
- Access to the dataset source (download URLs, APIs, etc.)
- Python development environment set up

---

## 🔧 Truncation Utilities Reference

The toolkit provides a dedicated truncation module with reusable functions for text processing:

### Core Functions

**`truncate_descriptions(descriptions, max_words, dataset, content_type)`**
- Truncate a dictionary of descriptions with dataset-aware limits
- `descriptions`: Dict mapping IDs to text descriptions
- `max_words`: Default word limit (overridden by dataset config)
- `dataset`: Dataset name for automatic limit lookup
- `content_type`: 'entity' or 'relation' for type-specific limits

**`truncate_text_by_words(text, max_words)`**
- Truncate a single text string by word count
- Uses whitespace splitting (SimKGC-compatible)

**`get_truncation_limit(dataset, content_type, default_limit)`**
- Get the appropriate word limit for a dataset and content type
- Returns default_limit if dataset/content_type not configured

### Configuration Functions

**`add_truncation_config(dataset, entity_limit, relation_limit)`**
- Add or update truncation limits for a dataset at runtime

**`get_available_datasets()`**
- List all datasets with configured truncation limits

**`get_dataset_config(dataset)`**
- Get the full configuration for a specific dataset

### Example Usage

```python
from text_kgc_data.truncation import (
    truncate_descriptions,
    truncate_text_by_words,
    add_truncation_config,
    get_truncation_limit
)

# Single text truncation
short_text = truncate_text_by_words("Very long description...", max_words=10)

# Dataset-aware truncation
entity_descs = truncate_descriptions(
    entity_id2description,
    dataset='wn18rr',
    content_type='entity'
)

# Add custom dataset configuration
add_truncation_config('my_dataset', entity_limit=40, relation_limit=20)

# Manual truncation with custom limit
manual_result = truncate_descriptions(descriptions, max_words=15)
```

---

## ⚙️ Advanced Dataset Implementation

The toolkit follows a modular architecture with clear separation of concerns:

```
text_kgc_data/
├── datasets/           # Dataset-specific modules
│   ├── __init__.py
│   ├── wn18rr.py      # Example: WN18RR implementation
│   ├── fb15k237.py    # Example: FB15k-237 implementation
│   ├── wikidata5m.py  # Example: Wikidata5M implementation
│   └── your_dataset.py # Your new dataset
├── processors.py       # Shared processing utilities
├── io.py              # File I/O utilities
└── cli.py             # Command-line interface
```

---

## 🛠️ Step-by-Step Implementation

### Step 1: Create Dataset Module

Create a new file `text_kgc_data/datasets/your_dataset.py`:

```python
"""Processing utilities for YourDataset knowledge graph."""

import os
import requests
from pathlib import Path
from typing import Dict, List, Tuple
from beartype import beartype
from tqdm import tqdm

from ..io import save_json, load_json, ensure_directory_exists
from ..truncation import truncate_descriptions, add_truncation_config


@beartype
def download_your_dataset(output_dir: str) -> Path:
    """Download YourDataset from official source.
    
    Args:
        output_dir: Directory to save downloaded files
        
    Returns:
        Path to downloaded data directory
    """
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    
    # Implement your download logic here
    # Example patterns:
    
    # For direct file downloads:
    files_to_download = {
        "train.txt": "https://example.com/train.txt",
        "valid.txt": "https://example.com/valid.txt", 
        "test.txt": "https://example.com/test.txt",
        "entities.txt": "https://example.com/entities.txt",
        "relations.txt": "https://example.com/relations.txt",
    }
    
    for filename, url in files_to_download.items():
        download_file(url, output_path / filename)
    
    return output_path


def download_file(url: str, output_path: Path) -> None:
    """Download a single file with progress bar."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as file, tqdm(
        desc=output_path.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = file.write(chunk)
            progress_bar.update(size)


@beartype
def load_your_dataset_entities(entities_file: Path) -> Dict[str, str]:
    """Load entity ID to name mappings from your dataset format.
    
    Args:
        entities_file: Path to entities file
        
    Returns:
        Dictionary mapping entity IDs to names
    """
    entity_id2name = {}
    
    with open(entities_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Adapt this parsing logic to your dataset format
            # Example for tab-separated: entity_id \t entity_name
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                entity_id, entity_name = parts[0], parts[1]
                entity_id2name[entity_id] = entity_name
    
    return entity_id2name


@beartype
def load_your_dataset_descriptions(descriptions_file: Path) -> Dict[str, str]:
    """Load entity ID to description mappings from your dataset format.
    
    Args:
        descriptions_file: Path to descriptions file
        
    Returns:
        Dictionary mapping entity IDs to descriptions
    """
    entity_id2description = {}
    
    with open(descriptions_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Adapt this parsing logic to your dataset format
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                entity_id, description = parts[0], parts[1]
                entity_id2description[entity_id] = description
    
    return entity_id2description


@beartype
def load_your_dataset_relations(relations_file: Path) -> Dict[str, str]:
    """Load relation ID to name mappings from your dataset format.
    
    Args:
        relations_file: Path to relations file
        
    Returns:
        Dictionary mapping relation IDs to names
    """
    relation_id2name = {}
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Adapt parsing logic to your format
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                relation_id, relation_name = parts[0], parts[1]
                # Apply any dataset-specific cleaning
                relation_name = clean_your_dataset_relation_name(relation_name)
                relation_id2name[relation_id] = relation_name
    
    return relation_id2name


def clean_your_dataset_relation_name(relation_name: str) -> str:
    """Apply dataset-specific cleaning to relation names.
    
    Args:
        relation_name: Raw relation name
        
    Returns:
        Cleaned relation name
    """
    # Apply your dataset-specific cleaning logic
    # Examples:
    # - Remove prefixes/namespaces
    # - Convert underscores to spaces
    # - Handle special characters
    cleaned = relation_name.replace('_', ' ').strip()
    return cleaned


@beartype
def process_your_dataset(
    data_dir: str,
    output_dir: str,
    entity_desc_max_words: int = 50,  # Adjust based on your dataset
    relation_desc_max_words: int = 30  # Adjust based on your dataset
) -> None:
    """Process YourDataset with SimKGC-compatible preprocessing.
    
    Args:
        data_dir: Directory containing raw dataset files
        output_dir: Directory to save processed files
        entity_desc_max_words: Maximum words for entity descriptions
        relation_desc_max_words: Maximum words for relation descriptions
    """
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    
    print("Loading YourDataset entities...")
    entity_id2name = load_your_dataset_entities(data_path / "entities.txt")
    
    print("Loading YourDataset descriptions...")
    entity_id2description = load_your_dataset_descriptions(data_path / "descriptions.txt")
    
    print("Loading YourDataset relations...")
    relation_id2name = load_your_dataset_relations(data_path / "relations.txt")
    
    # Apply SimKGC-compatible truncation using the new truncation module
    print("Truncating entity descriptions...")
    from ..truncation import truncate_descriptions
    entity_descriptions = truncate_descriptions(
        entity_id2description,
        max_words=entity_desc_max_words,
        dataset='yourdataset',  # Use your dataset name for automatic limits
        content_type='entity'
    )
    
    print("Truncating relation descriptions...")
    relation_names = truncate_descriptions(
        relation_id2name,
        max_words=relation_desc_max_words,
        dataset='yourdataset',
        content_type='relation'
    )
    
    # Save standardized outputs
    print("Saving processed files...")
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_descriptions, output_path / "entity_id2description.json")
    save_json(relation_names, output_path / "relation_id2name.json")
    
    # Save entity IDs list
    entity_ids = sorted(set(entity_id2name.keys()) | set(entity_id2description.keys()))
    with open(output_path / "entity_ids.txt", 'w', encoding='utf-8') as f:
        for entity_id in entity_ids:
            f.write(f"{entity_id}\n")
    
    print(f"YourDataset processing complete!")
    print(f"  - {len(entity_id2name)} entities")
    print(f"  - {len(relation_id2name)} relations")
    print(f"  - Output saved to: {output_path}")
```

### Step 2: Add CLI Commands

Update `text_kgc_data/cli.py` to include your dataset commands:

```python
# Add imports
from text_kgc_data.datasets.your_dataset import (
    download_your_dataset,
    process_your_dataset,
)

# Create dataset app
your_dataset_app = typer.Typer(help="YourDataset operations")
app.add_typer(your_dataset_app, name="yourdataset")

# Add download command
@your_dataset_app.command("download")
def your_dataset_download_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download YourDataset from official source."""
    try:
        typer.echo("Downloading YourDataset...")
        download_your_dataset(output_dir)
        typer.echo(f"✅ YourDataset downloaded to: {output_dir}")
    except Exception as e:
        typer.echo(f"❌ Error downloading YourDataset: {e}", err=True)
        raise typer.Exit(1)

# Add process command
@your_dataset_app.command("process")
def your_dataset_process_cmd(
    data_dir: str = typer.Argument(..., help="Directory containing raw YourDataset files"),
    output_dir: str = typer.Argument(..., help="Directory to save processed files"),
):
    """Process YourDataset with SimKGC-compatible preprocessing."""
    try:
        typer.echo("Processing YourDataset with SimKGC compatibility...")
        process_your_dataset(data_dir, output_dir)
        typer.echo(f"✅ YourDataset processing complete!")
    except Exception as e:
        typer.echo(f"❌ Error processing YourDataset: {e}", err=True)
        raise typer.Exit(1)
```

### Step 3: Update Batch Commands

Add your dataset to the batch processing commands in `cli.py`:

```python
# In download_all_cmd function, add:
typer.echo("\n📥 Downloading YourDataset...")
your_dataset_path = base_path / "yourdataset"
download_your_dataset(str(your_dataset_path))
typer.echo(f"✅ YourDataset downloaded to: {your_dataset_path}")

# In process_all_cmd function, add:
# Process YourDataset
your_dataset_raw = raw_base / "yourdataset"
your_dataset_output = output_base / "yourdataset"
if your_dataset_raw.exists():
    typer.echo("\n⚙️ Processing YourDataset...")
    process_your_dataset(str(your_dataset_raw), str(your_dataset_output))
    typer.echo(f"✅ YourDataset processed to: {your_dataset_output}")
    datasets_processed += 1
elif skip_missing:
    typer.echo(f"⚠️ Skipping YourDataset (not found at {your_dataset_raw})")
    datasets_skipped += 1
else:
    raise FileNotFoundError(f"YourDataset data not found at {your_dataset_raw}")
```

### Step 4: Add Dataset to Truncation Configuration

If your dataset needs special truncation limits, add them to the truncation configuration:

```python
# In your dataset module or during initialization
from ..truncation import add_truncation_config

# Add your dataset's truncation limits
add_truncation_config(
    'yourdataset',
    entity_limit=50,    # Words for entity descriptions
    relation_limit=25   # Words for relation descriptions
)
```

Alternatively, you can modify the default configuration in `text_kgc_data/truncation.py`:

```python
# Update TRUNCATION_CONFIGS in truncation.py
TRUNCATION_CONFIGS = {
    'wn18rr': {'entity': 50, 'relation': 30},
    'fb15k237': {'entity': 50, 'relation': 10}, 
    'wikidata5m': {'entity': 50, 'relation': 30},
    'yourdataset': {'entity': 50, 'relation': 25}  # Your limits
}
```

The new truncation module provides several advantages:
- **Reusable**: Functions can be used across different datasets
- **Configurable**: Easy to add new dataset-specific limits
- **Flexible**: Support for both dataset-aware and manual truncation
- **Backward Compatible**: Existing code continues to work

### Step 5: Create Documentation

Create `docs/yourdataset_example.md` following the pattern of existing documentation:

```markdown
# YourDataset Processing Guide

## Command Reference

| Command | Purpose |
|---------|---------|
| `text-kgc yourdataset download` | Download raw YourDataset |
| `text-kgc yourdataset process` | Complete SimKGC-compatible processing |

## Quick Start

**Single Dataset:**
```shell {.copy}
text-kgc yourdataset download data/raw/yourdataset
text-kgc yourdataset process data/raw/yourdataset data/standardised/yourdataset
```

**All Datasets (Recommended):**
```shell {.copy}
text-kgc download-and-process-all
```

## Dataset Specification
- **Source**: Your dataset source
- **Entities**: X unique entities
- **Relations**: Y semantic relations  
- **Splits**: train/validation/test triplet counts

## Paper-Ready Summary

*YourDataset Preprocessing:* We process YourDataset using SimKGC-compatible preprocessing...
```

Update `mkdocs.yml` to include your documentation:

```yaml
nav:
  - Overview: "index.md"
  - Standardised File Format: "standardised_tkg.md"
  - WN18RR Example: "wn18rr_example.md"
  - FB15k-237 Example: "fb15k237_example.md"
  - Wikidata5M Example: "wikidata5m_example.md"
  - YourDataset Example: "yourdataset_example.md"
  - Adding New Datasets: "adding_datasets.md"
```

---

## 🧪 Testing Your Implementation

### Basic Functionality Test

```shell
# Test download
text-kgc yourdataset download data/raw/yourdataset

# Test processing
text-kgc yourdataset process data/raw/yourdataset data/standardised/yourdataset

# Test batch operations
text-kgc download-all
text-kgc process-all
```

### Validate Output Structure

Ensure your processed data follows the standard format:

```python
from text_kgc_data.io import load_json

# Load and validate outputs
entity_id2name = load_json("data/standardised/yourdataset/entity_id2name.json")
entity_id2description = load_json("data/standardised/yourdataset/entity_id2description.json")
relation_id2name = load_json("data/standardised/yourdataset/relation_id2name.json")

# Verify structure
assert isinstance(entity_id2name, dict)
assert isinstance(entity_id2description, dict)
assert isinstance(relation_id2name, dict)

# Check for proper truncation
for desc in entity_id2description.values():
    if desc:  # Skip empty descriptions
        assert len(desc.split()) <= 50  # Or your entity limit
```

---

## 📝 Best Practices

### 1. **Follow Naming Conventions**
- Use lowercase with underscores: `your_dataset.py`
- CLI commands: `text-kgc yourdataset command`
- Function names: `download_your_dataset()`, `process_your_dataset()`

### 2. **Maintain SimKGC Compatibility**
- Use word-based truncation (not token-based)
- Apply appropriate word limits for your dataset
- Handle missing descriptions with empty strings

### 3. **Error Handling**
- Wrap operations in try-catch blocks
- Provide meaningful error messages
- Use `typer.Exit(1)` for CLI failures

### 4. **Documentation**
- Include docstrings for all functions
- Provide usage examples
- Create paper-ready summaries for academic use

### 5. **Code Quality**
- Use type hints with `@beartype` decorator
- Follow existing code style
- Add progress bars for long operations

---

## 🔄 Contributing Your Dataset

Once implemented, consider contributing back to the project:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b add-yourdataset`
3. **Implement your dataset** following this guide
4. **Add tests** for your implementation
5. **Update documentation**
6. **Submit a pull request**

### Pull Request Checklist

- [ ] Dataset module implemented in `datasets/yourdataset.py`
- [ ] CLI commands added to `cli.py`
- [ ] Batch commands updated to include new dataset
- [ ] Documentation created in `docs/yourdataset_example.md`
- [ ] Navigation updated in `mkdocs.yml`
- [ ] Tests pass for download and processing
- [ ] Output follows standardized JSON format
- [ ] SimKGC compatibility verified

---

## 🆘 Getting Help

If you encounter issues while adding a new dataset:

1. **Check existing implementations** in `datasets/` for patterns
2. **Review the processors module** for available utilities
3. **Test with small data samples** before full processing
4. **Open an issue** on GitHub for community support

---

## 📚 Additional Resources

- [SimKGC Paper](https://arxiv.org/abs/2203.02167) - Original methodology
- [Existing Dataset Implementations](../text_kgc_data_proj/text_kgc_data/datasets/) - Reference examples
- [CLI Architecture](../text_kgc_data_proj/text_kgc_data/cli.py) - Command structure
- [Processing Utilities](../text_kgc_data_proj/text_kgc_data/processors.py) - Shared functions

Happy coding! 🚀
