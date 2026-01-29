import re
from typing import List, Optional

def normalize_name(name: str) -> str:
    \"\"\"Clean and normalize a player name for matching.\"\"\"
    if not name:
        return \"\"
    # Remove suffixes (Jr, Sr, III, etc)
    name = re.sub(r'\\s+(jr|sr|iii|iv|v)\\.?$', '', name, flags=re.IGNORECASE)
    # Remove middle initials/names
    parts = name.split()
    if len(parts) > 2:
        name = f\"{parts[0]} {parts[-1]}\"
    # Remove special characters and lowercase
    return re.sub(r'[^a-zA-Z\\s]', '', name).lower().strip()

def names_match(name1: str, name2: str) -> bool:
    \"\"\"Check if two names match using fuzzy/normalized comparison.\"\"\"
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if norm1 == norm2:
        return True
        
    # Handle first initial + last name (e.g., \"M. Smith\" vs \"Mike Smith\")
    parts1 = norm1.split()
    parts2 = norm2.split()
    
    if len(parts1) == 2 and len(parts2) == 2:
        if parts1[1] == parts2[1]: # Last names match
            if parts1[0][0] == parts2[0][0]: # First initials match
                return True
                
    return False

def find_best_match(target_name: str, candidate_names: List[str]) -> Optional[str]:
    \"\"\"Find the best matching name from a list of candidates.\"\"\"
    for candidate in candidate_names:
        if names_match(target_name, candidate):
            return candidate
    return None
