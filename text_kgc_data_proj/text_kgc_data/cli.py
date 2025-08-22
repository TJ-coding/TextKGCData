"""Command-line interface for text-kgc-data toolkit."""

import os
from pathlib import Path
from typing import Optional
from unittest import result
import typer
from beartype import beartype

# Import dataset-specific functions
from text_kgc_data.datasets.wn18rr import (
    download_wn18rr,
    create_entity_id2name_wn18rr,
    create_entity_id2description_wn18rr,
    create_relation_id2name_wn18rr,
    create_entity_ids_wn18rr,
    process_wn18rr_dataset,
)
from text_kgc_data.datasets.wikidata5m import (
    download_wikidata5m,
    create_entity_id2name_wikidata5m,
    create_entity_id2description_wikidata5m,
    create_relation_id2name_wikidata5m,
    create_entity_ids_wikidata5m,
    download_wikidata5m_transductive,
    download_wikidata5m_inductive,
    process_wikidata5m_transductive,
    process_wikidata5m_inductive,
)
from text_kgc_data.datasets.fb15k237 import (
    download_fb15k237,
    process_fb15k237_dataset,
)
from text_kgc_data.processors import (
    fill_missing_entity_entries,
    truncate_entity_descriptions,
    validate_entity_mappings,
)
from text_kgc_data.truncation import (
    truncate_descriptions,
)
from text_kgc_data.io import (
    load_json,
    save_json,
    save_entity_ids_list,
    ensure_directory_exists,
)

app = typer.Typer(help="Text Knowledge Graph Completion Data Toolkit")

# Create subcommands for each dataset
wn18rr_app = typer.Typer(help="WN18RR dataset operations")
wikidata5m_app = typer.Typer(help="Wikidata5M dataset operations")
fb15k237_app = typer.Typer(help="FB15k-237 dataset operations")

app.add_typer(wn18rr_app, name="wn18rr")
app.add_typer(wikidata5m_app, name="wikidata5m")
app.add_typer(fb15k237_app, name="fb15k237")
app.add_typer(wikidata5m_app, name="wikidata5m")


# ===== WN18RR Commands =====

@wn18rr_app.command("download")
def wn18rr_download_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download WN18RR dataset from SimKGC repository."""
    output_path = Path(output_dir)
    data_path = download_wn18rr(output_path)
    typer.echo(f"✅ WN18RR data downloaded to: {data_path}")


@wn18rr_app.command("create-entity-text")
def wn18rr_create_entity_text_cmd(
    definitions_file: str = typer.Argument(..., help="Path to wordnet-mlj12-definitions.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create entity ID to name and description mappings from WN18RR definitions file."""
    definitions_path = Path(definitions_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Create mappings
    typer.echo("Creating entity_id2name mapping...")
    entity_id2name = create_entity_id2name_wn18rr(definitions_path)
    typer.echo("Creating entity_id2description mapping...")
    entity_id2description = create_entity_id2description_wn18rr(definitions_path)
    # Create entity IDs list
    typer.echo("Creating entity IDs list...")
    entity_ids = create_entity_ids_wn18rr(entity_id2name, entity_id2description)
    # Save files
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_entity_ids_list(entity_ids, output_path / "entity_ids.txt")
    typer.echo(f"✅ Entity mappings saved to: {output_path}")
    typer.echo(f"   - entity_id2name.json ({len(entity_id2name)} entities)")
    typer.echo(f"   - entity_id2description.json ({len(entity_id2description)} entities)")
    typer.echo(f"   - entity_ids.txt ({len(entity_ids)} entities)")


@wn18rr_app.command("create-relation-text")
def wn18rr_create_relation_text_cmd(
    relations_file: str = typer.Argument(..., help="Path to relations.dict"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create relation ID to name mappings from WN18RR relations file."""
    relations_path = Path(relations_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Create mapping
    typer.echo("Creating relation_id2name mapping...")
    relation_id2name = create_relation_id2name_wn18rr(relations_path)
    # Save file
    save_json(relation_id2name, output_path / "relation_id2name.json")
    typer.echo(f"✅ Relation mappings saved to: {output_path}")
    typer.echo(f"   - relation_id2name.json ({len(relation_id2name)} relations)")


@wn18rr_app.command("process-pipeline")
def wn18rr_process_pipeline_cmd(
    raw_data_dir: str = typer.Argument(..., help="Directory containing raw WN18RR data"),
    output_dir: str = typer.Argument(..., help="Directory to save processed data"),
    fill_missing: bool = typer.Option(True, help="Fill missing entity entries"),
    truncate_descriptions: bool = typer.Option(False, help="Truncate descriptions"),
    max_words: int = typer.Option(50, help="Maximum words for truncation (SimKGC-style)"),
):
    """Run complete WN18RR processing pipeline."""
    raw_path = Path(raw_data_dir)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Step 1: Create entity mappings
    typer.echo("Step 1: Creating entity mappings...")
    definitions_file = raw_path / "wordnet-mlj12-definitions.txt"
    entity_id2name = create_entity_id2name_wn18rr(definitions_file)
    entity_id2description = create_entity_id2description_wn18rr(definitions_file)
    # Step 2: Create relation mappings
    typer.echo("Step 2: Creating relation mappings...")
    relations_file = raw_path / "relations.dict"
    relation_id2name = create_relation_id2name_wn18rr(relations_file)
    # Step 3: Fill missing entries if requested
    if fill_missing:
        typer.echo("Step 3: Filling missing entity entries...")
        entity_id2name, entity_id2description = fill_missing_entity_entries(
            entity_id2name, entity_id2description
        )
    # Step 4: Truncate descriptions if requested
    if truncate_descriptions:
        typer.echo("Step 4: Truncating descriptions...")
        entity_id2description = truncate_descriptions(
            entity_id2description, max_words=max_words, 
            dataset='wn18rr', content_type='entity'
        )
    # Step 5: Save all outputs
    typer.echo("Step 5: Saving outputs...")
    entity_ids = create_entity_ids_wn18rr(entity_id2name, entity_id2description)
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_json(relation_id2name, output_path / "relation_id2name.json")
    save_entity_ids_list(entity_ids, output_path / "entity_ids.txt")
    typer.echo(f"✅ WN18RR pipeline completed successfully!")
    typer.echo(f"   Output saved to: {output_path}")
    typer.echo(f"   - {len(entity_ids)} entities")
    typer.echo(f"   - {len(relation_id2name)} relations")


# ===== Wikidata5M Commands =====

@wikidata5m_app.command("download")
def wikidata5m_download_cmd(
    output_dir: str = typer.Argument('data/raw/wikidata5m', help="Directory to save downloaded data"),
):
    """Download Wikidata5M dataset from SimKGC repository."""
    output_path = Path(output_dir)
    data_path = download_wikidata5m(output_path)
    typer.echo(f"✅ Wikidata5M data downloaded to: {data_path}")


@wikidata5m_app.command("create-entity-text")
def wikidata5m_create_entity_text_cmd(
    entity_names_file: str = typer.Argument(..., help="Path to wikidata5m_entity.txt"),
    entity_descriptions_file: str = typer.Argument(..., help="Path to wikidata5m_text.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create entity ID to name and description mappings from Wikidata5M files."""
    names_path = Path(entity_names_file)
    descriptions_path = Path(entity_descriptions_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Create mappings
    typer.echo("Creating entity_id2name mapping...")
    entity_id2name = create_entity_id2name_wikidata5m(names_path)
    typer.echo("Creating entity_id2description mapping...")
    entity_id2description = create_entity_id2description_wikidata5m(descriptions_path)
    # Create entity IDs list
    typer.echo("Creating entity IDs list...")
    entity_ids = create_entity_ids_wikidata5m(entity_id2name, entity_id2description)
    # Save files
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_entity_ids_list(entity_ids, output_path / "entity_ids.txt")
    typer.echo(f"✅ Entity mappings saved to: {output_path}")
    typer.echo(f"   - entity_id2name.json ({len(entity_id2name)} entities)")
    typer.echo(f"   - entity_id2description.json ({len(entity_id2description)} entities)")
    typer.echo(f"   - entity_ids.txt ({len(entity_ids)} entities)")


@wikidata5m_app.command("create-relation-text")
def wikidata5m_create_relation_text_cmd(
    relations_file: str = typer.Argument(..., help="Path to wikidata5m_relation.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create relation ID to name mappings from Wikidata5M relations file."""
    relations_path = Path(relations_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Create mapping
    typer.echo("Creating relation_id2name mapping...")
    relation_id2name = create_relation_id2name_wikidata5m(relations_path)
    # Save file
    save_json(relation_id2name, output_path / "relation_id2name.json")
    typer.echo(f"✅ Relation mappings saved to: {output_path}")
    typer.echo(f"   - relation_id2name.json ({len(relation_id2name)} relations)")


# ===== General Processing Commands =====

@app.command("fill-missing-entries")
def fill_missing_entries_cmd(
    entity_names_file: str = typer.Argument(..., help="Path to entity_id2name.json"),
    entity_descriptions_file: str = typer.Argument(..., help="Path to entity_id2description.json"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
    placeholder: str = typer.Option("-", help="Placeholder character for missing entries"),
):
    """Fill missing entries in entity mappings."""
    names_path = Path(entity_names_file)
    descriptions_path = Path(entity_descriptions_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Load data
    entity_id2name = load_json(names_path)
    entity_id2description = load_json(descriptions_path)
    # Fill missing entries
    typer.echo("Filling missing entity entries...")
    filled_names, filled_descriptions = fill_missing_entity_entries(
        entity_id2name, entity_id2description, placeholder
    )
    # Save results
    save_json(filled_names, output_path / "filled_entity_id2name.json")
    save_json(filled_descriptions, output_path / "filled_entity_id2description.json")
    typer.echo(f"✅ Missing entries filled and saved to: {output_path}")


@app.command("truncate-descriptions")
def truncate_descriptions_cmd(
    entity_descriptions_file: str = typer.Argument(..., help="Path to entity_id2description.json"),
    tokenizer_name: str = typer.Option("bert-base-uncased", help="HuggingFace tokenizer name (not used in word-based truncation)"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
    max_words: int = typer.Option(50, help="Maximum number of words (SimKGC-style)"),
    batch_size: int = typer.Option(50000, help="Batch size (not used in word-based truncation)"),
):
    """Truncate entity descriptions to specified word length (SimKGC-compatible)."""
    descriptions_path = Path(entity_descriptions_file)
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    # Load data
    entity_id2description = load_json(descriptions_path)
    # Truncate descriptions
    typer.echo(f"Truncating descriptions to {max_words} words (SimKGC-compatible)...")
    truncated_descriptions = truncate_descriptions(
        entity_id2description, max_words=max_words
    )
    # Save results
    save_json(truncated_descriptions, output_path / "truncated_entity_id2description.json")
    typer.echo(f"✅ Descriptions truncated and saved to: {output_path}")


@wn18rr_app.command("process")
def wn18rr_process_cmd(
    data_dir: str = typer.Argument('data/raw/wn18rr/WN18RR', help="Directory containing raw WN18RR files"),
    output_dir: str = typer.Argument('data/standardised/wn18rr', help="Directory to save processed files"),
):
    """Process WN18RR dataset with SimKGC-compatible preprocessing."""
    import shutil
    typer.echo("Processing WN18RR dataset with SimKGC compatibility...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    entity_id2name, entity_description2name, relation_id2name = process_wn18rr_dataset(data_dir)

    # Save results
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_description2name, output_path / "entity_description2name.json")
    save_json(relation_id2name, output_path / "relation_id2name.json")
    shutil.copy(Path(data_dir) / "train.txt", output_path / "train.tsv")
    shutil.copy(Path(data_dir) / "valid.txt", output_path / "valid.tsv")
    shutil.copy(Path(data_dir) / "test.txt", output_path / "test.tsv")
    typer.echo(f"✅ WN18RR processing complete!")
    


# ===== FB15k-237 Commands =====

@fb15k237_app.command("download")
def fb15k237_download_cmd(
    output_dir: str = typer.Argument('data/raw/fb15k237', help="Directory to save downloaded data"),
):
    """Download FB15k-237 dataset files."""
    typer.echo("Downloading FB15k-237 dataset...")
    download_fb15k237(output_dir)
    typer.echo(f"✅ FB15k-237 dataset downloaded to: {output_dir}")


@fb15k237_app.command("process")
def fb15k237_process_cmd(
    data_dir: str = typer.Argument('data/raw/fb15k237', help="Directory containing raw FB15k-237 files"),
    output_dir: str = typer.Argument('data/standardised/fb15k237', help="Directory to save processed files"),
):
    """Process FB15k-237 dataset with SimKGC-compatible preprocessing."""
    typer.echo("Processing FB15k-237 dataset with SimKGC compatibility...")
    from text_kgc_data.datasets.fb15k237 import preprocess_fb15k237_triplets
    import shutil
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    entity_id2name, entity_id2description, relation_id2name = preprocess_fb15k237_triplets(
        data_dir=data_dir,
        entity_desc_max_words=50,
        relation_desc_max_words=10
    )
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_json(relation_id2name, output_path / "relation_id2name.json")
    shutil.copy(Path(data_dir)/"train.txt", output_path / "train.tsv")
    shutil.copy(Path(data_dir)/"valid.txt", output_path / "valid.tsv")
    shutil.copy(Path(data_dir)/"test.txt", output_path / "test.tsv")
    typer.echo(f"✅ FB15k-237 processing complete! Outputs saved to: {output_path}")


# ===== Wikidata5M Transductive/Inductive Commands =====

@wikidata5m_app.command("download-transductive")
def wikidata5m_download_transductive_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download Wikidata5M transductive variant."""
    typer.echo("Downloading Wikidata5M transductive dataset...")
    download_wikidata5m_transductive(output_dir)
    typer.echo(f"✅ Wikidata5M transductive dataset downloaded to: {output_dir}")


@wikidata5m_app.command("download-inductive")
def wikidata5m_download_inductive_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download Wikidata5M inductive variant."""
    typer.echo("Downloading Wikidata5M inductive dataset...")
    download_wikidata5m_inductive(output_dir)
    typer.echo(f"✅ Wikidata5M inductive dataset downloaded to: {output_dir}")


@wikidata5m_app.command("process-transductive")
def wikidata5m_process_transductive_cmd(
    data_dir: str = typer.Argument('data/raw/wikidata5m', help="Directory containing raw Wikidata5M files"),
    output_dir: str = typer.Argument('data/standardised/wikidata5m-transductive', help="Directory to save processed files"),
):
    """Process Wikidata5M transductive dataset with SimKGC-compatible preprocessing."""
    typer.echo("Processing Wikidata5M transductive dataset with SimKGC compatibility...")
    from text_kgc_data.datasets.wikidata5m import preprocess_wikidata5m_transductive
    import shutil
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    entity_id2name, entity_id2description, relation_id2name = preprocess_wikidata5m_transductive(
        data_dir=data_dir,
        entity_desc_max_words=50,
        relation_desc_max_words=30
    )
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_json(relation_id2name, output_path / "relation_id2name.json")
    # Optionally copy raw splits for reference
    for split in ['train', 'valid', 'test']:
        src_file = Path(data_dir) / f"wikidata5m_transductive_{split}.txt"
        if src_file.exists():
            shutil.copy(src_file, output_path / f"{split}.tsv")
    typer.echo(f"✅ Wikidata5M transductive processing complete! Outputs saved to: {output_path}")


@wikidata5m_app.command("process-inductive")
def wikidata5m_process_inductive_cmd(
    data_dir: str = typer.Argument('data/raw/wikidata5m', help="Directory containing raw Wikidata5M files"),
    output_dir: str = typer.Argument('data/standardised/wikidata5m-inductive', help="Directory to save processed files"),
):
    """Process Wikidata5M inductive dataset with SimKGC-compatible preprocessing."""
    typer.echo("Processing Wikidata5M inductive dataset with SimKGC compatibility...")
    from text_kgc_data.datasets.wikidata5m import preprocess_wikidata5m_inductive
    import shutil
    output_path = Path(output_dir)
    ensure_directory_exists(output_path)
    entity_id2name, entity_id2description, relation_id2name = preprocess_wikidata5m_inductive(
        data_dir=data_dir,
        entity_desc_max_words=50,
        relation_desc_max_words=30
    )
    save_json(entity_id2name, output_path / "entity_id2name.json")
    save_json(entity_id2description, output_path / "entity_id2description.json")
    save_json(relation_id2name, output_path / "relation_id2name.json")
    # Optionally copy raw splits for reference
    for split in ['train', 'valid', 'test']:
        src_file = Path(data_dir) / f"wikidata5m_inductive_{split}.txt"
        if src_file.exists():
            shutil.copy(src_file, output_path / f"{split}.tsv")
    typer.echo(f"✅ Wikidata5M inductive processing complete! Outputs saved to: {output_path}")


def main():
    """Entry point for the CLI."""
    app()


# ===== Batch Processing Commands =====
@app.command("download-all")
def download_all_cmd(
    output_dir: str = typer.Argument("data/raw", help="Base directory to save all downloaded datasets"),
):
    """Download all datasets (WN18RR, FB15k-237, Wikidata5M transductive & inductive)."""
    base_path = Path(output_dir)
    typer.echo("🚀 Starting batch download of all datasets...")
    # Download WN18RR
    typer.echo("\n📥 Downloading WN18RR dataset...")
    wn18rr_path = base_path / "wn18rr"
    download_wn18rr(wn18rr_path)
    typer.echo(f"✅ WN18RR downloaded to: {wn18rr_path}")
    # Download FB15k-237
    typer.echo("\n📥 Downloading FB15k-237 dataset...")
    fb15k237_path = base_path / "fb15k237"
    download_fb15k237(str(fb15k237_path))
    typer.echo(f"✅ FB15k-237 downloaded to: {fb15k237_path}")
    # Download Wikidata5M transductive
    typer.echo("\n📥 Downloading Wikidata5M transductive dataset...")
    wikidata5m_trans_path = base_path / "wikidata5m-transductive"
    download_wikidata5m_transductive(str(wikidata5m_trans_path))
    typer.echo(f"✅ Wikidata5M transductive downloaded to: {wikidata5m_trans_path}")
    # Download Wikidata5M inductive
    typer.echo("\n📥 Downloading Wikidata5M inductive dataset...")
    wikidata5m_ind_path = base_path / "wikidata5m-inductive"
    download_wikidata5m_inductive(str(wikidata5m_ind_path))
    typer.echo(f"✅ Wikidata5M inductive downloaded to: {wikidata5m_ind_path}")
    typer.echo(f"\n🎉 All datasets downloaded successfully to: {base_path}")
    typer.echo("📁 Directory structure:")
    typer.echo(f"   {base_path}/wn18rr/")
    typer.echo(f"   {base_path}/fb15k237/") 
    typer.echo(f"   {base_path}/wikidata5m-transductive/")
    typer.echo(f"   {base_path}/wikidata5m-inductive/")


@app.command("process-all")
def process_all_cmd(
    raw_data_dir: str = typer.Argument("data/raw", help="Base directory containing all raw datasets"),
    output_dir: str = typer.Argument("data/standardised", help="Base directory to save all processed datasets"),
    skip_missing: bool = typer.Option(False, help="Skip datasets that don't exist instead of failing"),
):
    """Process all datasets with SimKGC-compatible preprocessing."""
    raw_base = Path(raw_data_dir)
    output_base = Path(output_dir)
    typer.echo("🚀 Starting batch processing of all datasets...")
    datasets_processed = 0
    datasets_skipped = 0
    # Process WN18RR
    wn18rr_raw = raw_base / "wn18rr/WN18RR"
    wn18rr_output = output_base / "wn18rr"
    if wn18rr_raw.exists():
        typer.echo("\n⚙️ Processing WN18RR dataset...")
        process_wn18rr_dataset(str(wn18rr_raw), str(wn18rr_output))
        typer.echo(f"✅ WN18RR processed to: {wn18rr_output}")
        datasets_processed += 1
    elif skip_missing:
        typer.echo(f"⚠️ Skipping WN18RR (not found at {wn18rr_raw})")
        datasets_skipped += 1
    else:
        raise FileNotFoundError(f"WN18RR data not found at {wn18rr_raw}")
    # Process FB15k-237
    fb15k237_raw = raw_base / "fb15k237"
    fb15k237_output = output_base / "fb15k237"
    if fb15k237_raw.exists():
        typer.echo("\n⚙️ Processing FB15k-237 dataset...")
        process_fb15k237_dataset(str(fb15k237_raw), str(fb15k237_output))
        typer.echo(f"✅ FB15k-237 processed to: {fb15k237_output}")
        datasets_processed += 1
    elif skip_missing:
        typer.echo(f"⚠️ Skipping FB15k-237 (not found at {fb15k237_raw})")
        datasets_skipped += 1
    else:
        raise FileNotFoundError(f"FB15k-237 data not found at {fb15k237_raw}")
    # Process Wikidata5M transductive
    wikidata5m_trans_raw = raw_base / "wikidata5m-transductive"
    wikidata5m_trans_output = output_base / "wikidata5m-transductive"
    if wikidata5m_trans_raw.exists():
        typer.echo("\n⚙️ Processing Wikidata5M transductive dataset...")
        process_wikidata5m_transductive(str(wikidata5m_trans_raw), str(wikidata5m_trans_output))
        typer.echo(f"✅ Wikidata5M transductive processed to: {wikidata5m_trans_output}")
        datasets_processed += 1
    elif skip_missing:
        typer.echo(f"⚠️ Skipping Wikidata5M transductive (not found at {wikidata5m_trans_raw})")
        datasets_skipped += 1
    else:
        raise FileNotFoundError(f"Wikidata5M transductive data not found at {wikidata5m_trans_raw}")
    # Process Wikidata5M inductive
    wikidata5m_ind_raw = raw_base / "wikidata5m-inductive"
    wikidata5m_ind_output = output_base / "wikidata5m-inductive"
    if wikidata5m_ind_raw.exists():
        typer.echo("\n⚙️ Processing Wikidata5M inductive dataset...")
        process_wikidata5m_inductive(str(wikidata5m_ind_raw), str(wikidata5m_ind_output))
        typer.echo(f"✅ Wikidata5M inductive processed to: {wikidata5m_ind_output}")
        datasets_processed += 1
    elif skip_missing:
        typer.echo(f"⚠️ Skipping Wikidata5M inductive (not found at {wikidata5m_ind_raw})")
        datasets_skipped += 1
    else:
        raise FileNotFoundError(f"Wikidata5M inductive data not found at {wikidata5m_ind_raw}")
    typer.echo(f"\n🎉 Batch processing completed!")
    typer.echo(f"📊 Summary: {datasets_processed} processed, {datasets_skipped} skipped")
    if datasets_processed > 0:
        typer.echo(f"📁 Processed datasets saved to: {output_base}")


@app.command("download-and-process-all")
def download_and_process_all_cmd(
    raw_data_dir: str = typer.Argument("data/raw", help="Directory to save downloaded datasets"),
    output_dir: str = typer.Argument("data/standardised", help="Directory to save processed datasets"),
):
    """Download and process all datasets in one command (complete pipeline)."""
    typer.echo("🚀 Starting complete pipeline: download + process all datasets...")
    # Step 1: Download all datasets
    typer.echo("\n" + "="*60)
    typer.echo("📥 PHASE 1: DOWNLOADING ALL DATASETS")
    typer.echo("="*60)
    download_all_cmd.callback(raw_data_dir)
    # Step 2: Process all datasets
    typer.echo("\n" + "="*60)
    typer.echo("⚙️ PHASE 2: PROCESSING ALL DATASETS")
    typer.echo("="*60)
    process_all_cmd.callback(raw_data_dir, output_dir, skip_missing=False)
    typer.echo("\n" + "="*60)
    typer.echo("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY!")
    typer.echo("="*60)
    typer.echo(f"📁 Raw data: {raw_data_dir}")
    typer.echo(f"📁 Processed data: {output_dir}")
    typer.echo("\n💡 You can now use the processed datasets for training!")


if __name__ == "__main__":
    main()
