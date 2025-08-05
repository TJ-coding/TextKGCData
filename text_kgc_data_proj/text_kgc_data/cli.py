"""Command-line interface for text-kgc-data toolkit."""

from pathlib import Path
from typing import Optional
import typer
from beartype import beartype

# Import dataset-specific functions
from text_kgc_data.datasets.wn18rr import (
    download_wn18rr,
    create_entity_id2name_wn18rr,
    create_entity_id2description_wn18rr,
    create_relation_id2name_wn18rr,
    create_entity_ids_wn18rr,
)
from text_kgc_data.datasets.wikidata5m import (
    download_wikidata5m,
    create_entity_id2name_wikidata5m,
    create_entity_id2description_wikidata5m,
    create_relation_id2name_wikidata5m,
    create_entity_ids_wikidata5m,
)
from text_kgc_data.processors import (
    fill_missing_entity_entries,
    truncate_entity_descriptions,
    validate_entity_mappings,
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

app.add_typer(wn18rr_app, name="wn18rr")
app.add_typer(wikidata5m_app, name="wikidata5m")


# ===== WN18RR Commands =====

@wn18rr_app.command("download")
def wn18rr_download_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download WN18RR dataset from SimKGC repository."""
    try:
        output_path = Path(output_dir)
        data_path = download_wn18rr(output_path)
        typer.echo(f"✅ WN18RR data downloaded to: {data_path}")
    except Exception as e:
        typer.echo(f"❌ Error downloading WN18RR: {e}", err=True)
        raise typer.Exit(1)


@wn18rr_app.command("create-entity-mappings")
def wn18rr_create_entity_mappings_cmd(
    definitions_file: str = typer.Argument(..., help="Path to wordnet-mlj12-definitions.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create entity ID to name and description mappings from WN18RR definitions file."""
    try:
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
        
    except Exception as e:
        typer.echo(f"❌ Error creating entity mappings: {e}", err=True)
        raise typer.Exit(1)


@wn18rr_app.command("create-relation-mappings")
def wn18rr_create_relation_mappings_cmd(
    relations_file: str = typer.Argument(..., help="Path to relations.dict"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create relation ID to name mappings from WN18RR relations file."""
    try:
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
        
    except Exception as e:
        typer.echo(f"❌ Error creating relation mappings: {e}", err=True)
        raise typer.Exit(1)


@wn18rr_app.command("process-pipeline")
def wn18rr_process_pipeline_cmd(
    raw_data_dir: str = typer.Argument(..., help="Directory containing raw WN18RR data"),
    output_dir: str = typer.Argument(..., help="Directory to save processed data"),
    fill_missing: bool = typer.Option(True, help="Fill missing entity entries"),
    truncate_descriptions: bool = typer.Option(False, help="Truncate descriptions"),
    tokenizer_name: Optional[str] = typer.Option(None, help="Tokenizer for truncation"),
    max_tokens: int = typer.Option(50, help="Maximum tokens for truncation"),
):
    """Run complete WN18RR processing pipeline."""
    try:
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
            if not tokenizer_name:
                typer.echo("❌ Tokenizer name required for description truncation", err=True)
                raise typer.Exit(1)
            
            typer.echo("Step 4: Truncating descriptions...")
            entity_id2description = truncate_entity_descriptions(
                entity_id2description, tokenizer_name, max_tokens
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
        
    except Exception as e:
        typer.echo(f"❌ Error in WN18RR pipeline: {e}", err=True)
        raise typer.Exit(1)


# ===== Wikidata5M Commands =====

@wikidata5m_app.command("download")
def wikidata5m_download_cmd(
    output_dir: str = typer.Argument(..., help="Directory to save downloaded data"),
):
    """Download Wikidata5M dataset from SimKGC repository."""
    try:
        output_path = Path(output_dir)
        data_path = download_wikidata5m(output_path)
        typer.echo(f"✅ Wikidata5M data downloaded to: {data_path}")
    except Exception as e:
        typer.echo(f"❌ Error downloading Wikidata5M: {e}", err=True)
        raise typer.Exit(1)


@wikidata5m_app.command("create-entity-mappings")
def wikidata5m_create_entity_mappings_cmd(
    entity_names_file: str = typer.Argument(..., help="Path to wikidata5m_entity.txt"),
    entity_descriptions_file: str = typer.Argument(..., help="Path to wikidata5m_text.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create entity ID to name and description mappings from Wikidata5M files."""
    try:
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
        
    except Exception as e:
        typer.echo(f"❌ Error creating entity mappings: {e}", err=True)
        raise typer.Exit(1)


@wikidata5m_app.command("create-relation-mappings")
def wikidata5m_create_relation_mappings_cmd(
    relations_file: str = typer.Argument(..., help="Path to wikidata5m_relation.txt"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
):
    """Create relation ID to name mappings from Wikidata5M relations file."""
    try:
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
        
    except Exception as e:
        typer.echo(f"❌ Error creating relation mappings: {e}", err=True)
        raise typer.Exit(1)


# ===== General Processing Commands =====

@app.command("fill-missing-entries")
def fill_missing_entries_cmd(
    entity_names_file: str = typer.Argument(..., help="Path to entity_id2name.json"),
    entity_descriptions_file: str = typer.Argument(..., help="Path to entity_id2description.json"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
    placeholder: str = typer.Option("-", help="Placeholder character for missing entries"),
):
    """Fill missing entries in entity mappings."""
    try:
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
        
    except Exception as e:
        typer.echo(f"❌ Error filling missing entries: {e}", err=True)
        raise typer.Exit(1)


@app.command("truncate-descriptions")
def truncate_descriptions_cmd(
    entity_descriptions_file: str = typer.Argument(..., help="Path to entity_id2description.json"),
    tokenizer_name: str = typer.Argument(..., help="HuggingFace tokenizer name"),
    output_dir: str = typer.Argument(..., help="Directory to save output files"),
    max_tokens: int = typer.Option(50, help="Maximum number of tokens"),
    batch_size: int = typer.Option(50000, help="Batch size for processing"),
):
    """Truncate entity descriptions to specified token length."""
    try:
        descriptions_path = Path(entity_descriptions_file)
        output_path = Path(output_dir)
        ensure_directory_exists(output_path)
        
        # Load data
        entity_id2description = load_json(descriptions_path)
        
        # Truncate descriptions
        typer.echo(f"Truncating descriptions to {max_tokens} tokens using {tokenizer_name}...")
        truncated_descriptions = truncate_entity_descriptions(
            entity_id2description, tokenizer_name, max_tokens, batch_size
        )
        
        # Save results
        save_json(truncated_descriptions, output_path / "truncated_entity_id2description.json")
        
        typer.echo(f"✅ Descriptions truncated and saved to: {output_path}")
        
    except Exception as e:
        typer.echo(f"❌ Error truncating descriptions: {e}", err=True)
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
