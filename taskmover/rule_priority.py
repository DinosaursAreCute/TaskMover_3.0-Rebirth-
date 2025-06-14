import uuid

def get_sorted_rule_keys(rules):
    """
    Return a list of rule keys sorted by their priority (ascending), then by creation (id) for stability.
    """
    return sorted(
        rules.keys(),
        key=lambda k: (rules[k].get('priority', 0), rules[k].get('id', ''))
    )

def move_rule_priority(rules, rule_key, direction):
    """
    Move a rule up or down in priority. Direction is +1 (down) or -1 (up).
    Adjusts priorities and returns True if changed.
    """
    sorted_keys = get_sorted_rule_keys(rules)
    idx = sorted_keys.index(rule_key)
    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(sorted_keys):
        return False  # Out of bounds
    # Swap priorities
    key2 = sorted_keys[new_idx]
    p1 = rules[rule_key].get('priority', 0)
    p2 = rules[key2].get('priority', 0)
    rules[rule_key]['priority'], rules[key2]['priority'] = p2, p1
    return True

def set_rule_priority(rules, rule_key, new_priority):
    """
    Set a rule's priority and reassign priorities to keep them unique and ordered.
    """
    rules[rule_key]['priority'] = new_priority
    # Reassign priorities to be unique and ordered
    sorted_keys = sorted(rules.keys(), key=lambda k: (rules[k]['priority'], rules[k].get('id', '')))
    for i, k in enumerate(sorted_keys):
        rules[k]['priority'] = i

# Optionally, add more advanced logic here in the future.
