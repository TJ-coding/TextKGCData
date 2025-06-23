from abc import ABC
from dataclasses import dataclass
from typing import Dict

@dataclass
class TextualKG(ABC):
    '''An interface for a textual knowledge graph.'''
    entity_id2name: Dict[str, str]
    entity_id2description: Dict[str, str]
    relation_id2name: Dict[str, str]