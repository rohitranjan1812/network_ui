#!/usr/bin/env python3
"""
Fix specific remaining linting issues after automated cleanup.
"""

import os
import re


def fix_continuation_lines(file_path):
    """Fix specific continuation line indentation issues."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix specific E128 issues
    # models.py line 115
    content = re.sub(
        r'self\.edges = \[edge for edge in self\.edges\n\s*if edge\.source',
        'self.edges = [edge for edge in self.edges\n                      if edge.source',
        content
    )
    
    # Fix models.py line 366
    content = re.sub(
        r'errors\.append\(f"Invalid node ID: \{node_id\}"\)\n\s*continue',
        'errors.append(f"Invalid node ID: {node_id}")\n                    continue',
        content
    )
    
    # Fix E131 hanging indent issues
    content = re.sub(
        r'__all__ = \[\n\s*"Node",',
        '__all__ = [\n    "Node",',
        content
    )
    
    return content if content != original_content else None


def fix_unused_imports(file_path):
    """Remove specific unused imports that are actually not used."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove specific unused imports
    filtered_lines = []
    for line in lines:
        # Skip these specific unused imports
        if any(pattern in line.strip() for pattern in [
            'from datetime import datetime, date',
            'from typing import Optional, Tuple',
            'from typing import Tuple, Set',
            'from typing import Tuple',
            'import json',
            'from typing import List, Optional',
            '..config.LayoutAlgorithm',
            '..config.RenderingEngine'
        ]):
            continue
        filtered_lines.append(line)
    
    return ''.join(filtered_lines)


def process_file(file_path):
    """Process a single file."""
    print(f"Processing: {file_path}")
    
    try:
        # Fix continuation lines
        new_content = fix_continuation_lines(file_path)
        
        if new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Fixed continuation lines: {file_path}")
        
        # Fix unused imports
        if any(x in file_path for x in ['visualization', 'api']):
            new_content = fix_unused_imports(file_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Fixed unused imports: {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")


def main():
    """Main function."""
    files_to_fix = [
        'src/network_ui/core/models.py',
        'src/network_ui/core/transformers.py',
        'src/network_ui/core/validators.py',
        'src/network_ui/__init__.py',
        'src/network_ui/core/__init__.py',
        'src/network_ui/visualization/__init__.py',
        'src/network_ui/visualization/api/visualization.py',
        'src/network_ui/visualization/config.py',
        'src/network_ui/visualization/interactions.py',
        'src/network_ui/visualization/layouts.py',
        'src/network_ui/api/graph_engine.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            process_file(file_path)


if __name__ == "__main__":
    main() 