from typer import Typer
from beartype import beartype
from text_kgc_data.download_data import download_simkgc_data
from text_kgc_data.standardise_tkg_files.standardise_wn18rr import (
    standardize_wn18rr_entity_files,
    standardize_wn18rr_relation_file,
)
from text_kgc_data.standardise_tkg_files.standardise_wikidata5m import (
    standardize_wikidata5m_entity_files,
    standardize_wikidata5m_relation_file,
)
from text_kgc_data.preprocessors import (
    fill_missing_entries,
    truncate_description,
)

app = Typer()

@app.command()
@beartype
def download_text_kgc_dataset(data_dir_name="text_based_kgc_data"):
    """Downloads the text-based KGC dataset from SimKGC repository."""
    download_simkgc_data(data_dir_name=data_dir_name)

@app.command()
@beartype
def standardize_wn18rr_entity_files_cli(
    definitions_source_path: str = "WN18RR/wordnet-mlj12-definitions.txt",
    entity_id_save_path: str = "wn18rr_tkg/entity_ids.txt",
    entity_id2name_save_path: str = "wn18rr_tkg/entity_id2_name.txt",
    entity_id2description_save_path: str = "wn18rr_tkg/entity_id2_description.txt",
):
    """Standardize WN18RR entity files."""
    standardize_wn18rr_entity_files(
        definitions_source_path=definitions_source_path,
        entity_id_save_path=entity_id_save_path,
        entity_id2name_save_path=entity_id2name_save_path,
        entity_id2description_save_path=entity_id2description_save_path,
    )

@app.command()
@beartype
def standardize_wn18rr_relation_file_cli(
    relations_source_path: str = "WN18RR/relations.dict",
    relation_id2name_save_path: str = "wn18rr_tkg/wn18rr-relations2description.json",
):
    """Standardize WN18RR relation file."""
    standardize_wn18rr_relation_file(
        relations_source_path=relations_source_path,
        relation_id2name_save_path=relation_id2name_save_path,
    )

@app.command()
@beartype
def standardize_wikidata5m_entity_files_cli(
    entity_names_source_path: str = "wikidata5m/wikidata5m_entity.txt",
    entity_descriptions_source_path: str = "wikidata5m/wikidata5m_text.txt",
    entity_id_save_path: str = "wikidata5m_tkg/entity_ids.txt",
    entity_id2name_save_path: str = "wikidata5m_tkg/entity_id2_name.json",
    entity_id2description_save_path: str = "wikidata5m_tkg/entity_id2_description.json",
):
    """Standardize Wikidata5M entity files."""
    standardize_wikidata5m_entity_files(
        entity_names_source_path=entity_names_source_path,
        entity_descriptions_source_path=entity_descriptions_source_path,
        entity_id_save_path=entity_id_save_path,
        entity_id2name_save_path=entity_id2name_save_path,
        entity_id2description_save_path=entity_id2description_save_path,
    )

@app.command()
@beartype
def standardize_wikidata5m_relation_file_cli(
    relations_source_path: str = "wikidata5m/wikidata5m_relation.txt",
    relation_id2name_save_path: str = "wikidata5m_tkg/relation_id2name.json",
):
    """Standardize Wikidata5M relation file."""
    standardize_wikidata5m_relation_file(
        relations_source_path=relations_source_path,
        relation_id2name_save_path=relation_id2name_save_path,
    )

@app.command()
@beartype
def fill_missing_entries_cli(
    entity_id2name_source_path: str,
    entity_id2description_source_ath: str,
    entity_id2name_save_path: str,
    entity_id2description_save_path: str,
    place_holder_character: str = '-',
):
    """Fill missing entries in entity_id2name and entity_id2description JSON files and save results."""
    import json
    with open(entity_id2name_source_path, 'r') as f:
        entity_id2name = json.load(f)
    with open(entity_id2description_source_ath, 'r') as f:
        entity_id2description = json.load(f)
    entity_id2name, entity_id2description = fill_missing_entries(
        entity_id2name, entity_id2description, place_holder_character=place_holder_character
    )
    with open(entity_id2name_save_path, 'w') as f:
        json.dump(entity_id2name, f, indent=4)
    with open(entity_id2description_save_path, 'w') as f:
        json.dump(entity_id2description, f, indent=4)

@app.command()
@beartype
def truncate_description_cli(
    tokenizer_name: str,
    entity_id2description_path: str= "wn18rr_tkg/entity_id2_description.json",
    output_entity_id2description_path: str= "wn18rr_tkg/truncated_entity_id2_description.json",
    truncate_tokens: int = 50,
    batch_size: int = 50000,
):
    """Truncate entity descriptions in a JSON file and save the result. Note: The SimKGC paper sets truncation to 50 tokens."""
    import json
    with open(entity_id2description_path, 'r') as f:
        entity_id2description = json.load(f)
    entity_id2description = truncate_description(
        entity_id2description,
        tokenizer_name=tokenizer_name,
        truncate_tokens=truncate_tokens,
        batch_size=batch_size,
    )
    with open(output_entity_id2description_path, 'w') as f:
        json.dump(entity_id2description, f, indent=4)

def none():
    pass

app()
