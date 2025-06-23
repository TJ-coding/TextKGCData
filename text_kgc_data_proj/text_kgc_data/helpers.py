from typing import List, Tuple
from beartype import beartype
from tqdm import tqdm

@beartype
def text_to_tsvs(tsv_text: str) -> List[Tuple[str, ...]]:
    '''Convers a text representation of tsv triplets into a list of tuples.'''
    lines: List[str] = tsv_text.strip().split("\n")
    tsvs: List[Tuple[str, str, str]] = [
        tuple([i.strip() for i in line.split("\t")]) for line in lines
    ]
    return tsvs

@beartype
def tsv_tuples_to_text(tsvs: List[Tuple[str, str]]) -> str:
    '''Converts a list of tsv tuples into a text representation.'''
    text = ""
    for tsv in tqdm(tsvs, total=len(tsvs)):
        text += "\t".join(tsv) + "\n"
    text.strip()
    return text