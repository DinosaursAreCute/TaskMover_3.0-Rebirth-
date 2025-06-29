#!/usr/bin/env python3
"""Fix imports in example files."""

import os
import re
from pathlib import Path

def fix_example_file(file_path):
    """Fix imports in a single example file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add sys path manipulation at the top
    if 'sys.path.insert' not in content:
        imports_start = content.find('import tkinter')
        if imports_start == -1:
            imports_start = content.find('import')
        
        if imports_start != -1:
            sys_path_code = '''import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

'''
            content = content[:imports_start] + sys_path_code + content[imports_start:]
    
    # Fix import patterns
    replacements = [
        (r'from ui\.(\w+)', r'from taskmover.ui.\1'),
        (r'tk\.messagebox\.', 'messagebox.'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Add messagebox import if needed
    if 'messagebox.' in content and 'from tkinter import messagebox' not in content:
        # Find the last import line
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
        if import_lines:
            last_import = import_lines[-1]
            content = content.replace(last_import, last_import + '\nfrom tkinter import messagebox')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Fix all example files."""
    examples_dir = Path('docs/ui_components/examples')
    
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return
    
    for py_file in examples_dir.glob('*.py'):
        print(f"Fixing {py_file}")
        try:
            fix_example_file(py_file)
        except Exception as e:
            print(f"Error fixing {py_file}: {e}")

if __name__ == '__main__':
    main()
