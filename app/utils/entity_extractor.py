import spacy
from typing import List

# Load the English language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback to simple keyword extraction if spaCy model is not available
    nlp = None

def extract_named_entities(text: str) -> List[str]:
    """
    Extract named entities (PERSON, ORG) from text.
    Falls back to simple keyword extraction if spaCy is not available.
    
    Args:
        text (str): Input text to extract entities from
        
    Returns:
        List[str]: List of extracted entity texts
    """
    if nlp is None:
        # Simple fallback - split on spaces and take capitalized words
        words = text.split()
        return [word for word in words if word[0].isupper()]
        
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG")] 