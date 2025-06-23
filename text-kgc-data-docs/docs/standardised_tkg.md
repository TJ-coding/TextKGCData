# Standardised Files for Text-Based Knowledge Graph Data

A "standardised file" format is used in this project to store knowledge graph (KG) data with rich textual information in a way that is easy to process, share, and load into models. This format ensures consistency across datasets and tools, making it simple to use different KGs with the same codebase.

---

## Why Standardise?
- **Interoperability**: Use the same loader and processing code for different datasets (e.g., WN18RR, Wikidata5M).
- **Clarity**: Each file has a clear, single purpose (IDs, names, descriptions, relations).
- **Extensibility**: Easy to add new datasets or fields.

---

## Standardised File Types

### 1. `entity_ids.txt`
A plain text file with one entity ID per line.

**Example:**
```
Q42
Q123
Q999
```

### 2. `entity_id2_name.json`
A JSON dictionary mapping each entity ID to its canonical name.

**Example:**
```json
{
  "Q42": "Douglas Adams",
  "Q123": "Example Entity",
  "Q999": "Another Entity"
}
```

### 3. `entity_id2_description.json`
A JSON dictionary mapping each entity ID to a textual description.

**Example:**
```json
{
  "Q42": "Douglas Adams was an English author, best known for The Hitchhiker's Guide to the Galaxy.",
  "Q123": "This is a sample entity used for demonstration purposes.",
  "Q999": "A placeholder entity in the knowledge graph."
}
```

### 4. `relation_id2name.json` (or `relation_id2description.json`)
A JSON dictionary mapping each relation ID to its name or description.

**Example:**
```json
{
  "P31": "instance of",
  "P279": "subclass of",
  "P50": "author"
}
```

---

## Typical Directory Structure

```
<dataset>_tkg/
    entity_ids.txt
    entity_id2_name.json
    entity_id2_description.json
    relation_id2name.json
```

---

## Notes
- All files use UTF-8 encoding.
- JSON files are formatted for readability (indentation).
- The same format is used for all supported datasets, enabling unified loading and processing.

---

## Usage
These files can be loaded directly using the provided Python loaders, or processed further for downstream tasks such as training text-based KGC models.
