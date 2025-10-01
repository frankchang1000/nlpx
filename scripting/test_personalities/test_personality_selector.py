
# PERSONALITY RANDOM SELECTOR FUNCTIONS
# Generated from 5 personalities

import random
import json

def load_personalities(json_path):
    """Load personalities from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

def random_personality(personalities, filters=None):
    """
    Get a random personality with optional filters.
    
    filters example:
    {
        'social_level': 'introvert',
        'age_range': '20-25', 
        'suitable_roles': ['whiskey_enthusiast'],
        'complexity_score': [4, 5],  # list means "any of these values"
        'tags': ['depression', 'anxiety']  # must contain ANY of these tags
    }
    """
    candidates = personalities
    
    if filters:
        for key, value in filters.items():
            if key == 'complexity_score' and isinstance(value, list):
                candidates = [p for p in candidates if p.get(key, 0) in value]
            elif key == 'suitable_roles' and isinstance(value, list):
                candidates = [p for p in candidates if any(role in p.get(key, []) for role in value)]
            elif key == 'tags' and isinstance(value, list):
                candidates = [p for p in candidates if any(tag in p.get('personality_tags', []) for tag in value)]
            else:
                candidates = [p for p in candidates if p.get(key) == value]
    
    return random.choice(candidates) if candidates else None

def get_personalities_by_role(personalities, role):
    """Get all personalities suitable for a specific role."""
    return [p for p in personalities if role in p.get('suitable_for_roles', [])]

def get_diverse_set(personalities, count=3):
    """Get a diverse set of personalities with different traits."""
    if len(personalities) < count:
        return personalities
    
    selected = []
    used_traits = set()
    
    # First, try to get personalities with different core traits
    for p in personalities:
        if len(selected) >= count:
            break
        
        p_traits = set(p.get('core_traits_list', []))
        if not p_traits.intersection(used_traits):
            selected.append(p)
            used_traits.update(p_traits)
    
    # Fill remaining slots randomly
    remaining = [p for p in personalities if p not in selected]
    while len(selected) < count and remaining:
        selected.append(random.choice(remaining))
        remaining.remove(selected[-1])
    
    return selected

# EXAMPLE USAGE:
# personalities = load_personalities('all_personalities.json')
# 
# # Get a random whiskey enthusiast
# whiskey_person = random_personality(personalities, {'suitable_roles': ['whiskey_enthusiast']})
# 
# # Get an introverted young adult
# introvert = random_personality(personalities, {'social_level': 'introvert', 'age_range': '20-25'})
# 
# # Get 3 diverse personalities
# diverse_group = get_diverse_set(personalities, 3)

# AVAILABLE FILTERS:
# - social_level: {'ambivert'}
# - age_range: {'unknown'}
# - complexity_score: {2}
# - suitable_roles: set()
# - source_type: {'mixed'}
