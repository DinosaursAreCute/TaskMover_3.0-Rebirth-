import re

# Read the file
with open('taskmover/ui/navigation_components.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace font weight tokens with string literals
replacements = [
    (r'tokens\.fonts\[\"weight_semibold\"\]', '"normal"'),
    (r'tokens\.fonts\[\"weight_bold\"\]', '"bold"'),
    (r'tokens\.fonts\[\"weight_normal\"\]', '"normal"')
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('taskmover/ui/navigation_components.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Font tokens replaced successfully')
