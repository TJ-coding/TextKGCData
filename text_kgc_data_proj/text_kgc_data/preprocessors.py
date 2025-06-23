from typing import List, Dict, Tuple
from beartype import beartype
from tqdm import tqdm
from transformers import AutoTokenizer

@beartype    
def fill_missing_entries(entity_id2name: Dict[str, str], entity_id2description: Dict[str, str], 
                         place_holder_character: str = '-')->Tuple[Dict[str, str], Dict[str, str]]:
    '''Fills missing entries in the entity_id2name and entity_id2description dictionaries with a placeholder character.'''
    entity_ids_with_name: set[str] = set(entity_id2name.keys())
    entity_ids_with_desc: set[str] = set(entity_id2description.keys())

    entity_ids_with_missing_name: set[str] = entity_ids_with_desc - entity_ids_with_name
    entity_ids_with_missing_desc: set[str] = entity_ids_with_name - entity_ids_with_desc
    
    for entity_id in entity_ids_with_missing_name:
        entity_id2name[entity_id] = place_holder_character
    for entity_id in entity_ids_with_missing_desc:
        entity_id2description[entity_id] = place_holder_character    
    return (entity_id2name, entity_id2description)

@beartype
def truncate_description(entity_id2description: Dict[str, str], tokenizer_name:str, 
                        truncate_tokens: int = 50, batch_size=50000) -> Dict[str, str]:
    '''Truncates entity description to a maximum number of words. The SimKGC paper sets truncation to 50 tokens.'''
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    entity_ids: List[str] = list(entity_id2description.keys())
    description: List[str] = list(entity_id2description.values())
    
    batched_description: List[List[str]] = [description[i:i + batch_size] for i in range(0, len(description), batch_size)]
    
    batched_truncated_tokens: List[List[int]] = []
    # Truncate to 50 tokens        
    for batch in tqdm(batched_description, desc="Truncating description", total=len(batched_description)):
        tokens = tokenizer.batch_encode_plus(
            batch, 
            add_special_tokens=False, 
            return_attention_mask=False, 
            return_tensors=None,
            truncation=True,
            max_length=truncate_tokens
        )['input_ids']
        batched_truncated_tokens.append(tokens)
    for tokens in tqdm(batched_truncated_tokens, desc="Converting tokens to strings", total=len(batched_truncated_tokens)):
        # Convert tokens back to strings
        tokens = tokenizer.batch_decode(tokens, skip_special_tokens=True)
        # Truncate to 50 tokens if necessary
        entity_id2description = {entity_ids[i]: tokens[i] for i in range(len(tokens))}
    return entity_id2description