import re

# Read the file
with open('taskmover/ui/navigation_components.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix font tuple issues - need to convert string size to int
content = re.sub(r'tokens\.fonts\["size_(\w+)"\]', r'int(tokens.fonts["size_\1"])', content)

# Write back
with open('taskmover/ui/navigation_components.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Font size conversions fixed in navigation_components.py')
