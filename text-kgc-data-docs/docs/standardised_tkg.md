# Standardised File Format

TextKGCData uses a standardised file format for knowledge graph data with textual descriptions.

---

## File Types

### `entity_ids.txt`
Plain text file with one entity ID per line.
```
Q42
Q123
Q999
```

### `entity_id2_name.json`
JSON mapping entity IDs to names.
```json
{
  "Q42": "Douglas Adams",
  "Q123": "Example Entity"
}
```

### `entity_id2_description.json`
JSON mapping entity IDs to descriptions.
```json
{
  "Q42": "Douglas Adams was an English author, best known for The Hitchhiker's Guide to the Galaxy.",
  "Q123": "This is a sample entity used for demonstration purposes."
}
```

### `relation_id2name.json`
JSON mapping relation IDs to names.
```json
{
  "P31": "instance of",
  "P279": "subclass of",
  "P50": "author"
}
```

---

## Directory Structure

```
<dataset>_standardized_/
    entity_ids.txt
    entity_id2_name.json
    entity_id2_description.json
    relation_id2name.json
```
