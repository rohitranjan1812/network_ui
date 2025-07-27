#!/usr/bin/env python3
"""
Script to fix common linting issues in the Network UI codebase.
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Fix common linting issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Fix blank lines with whitespace
        content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
        
        # Fix missing whitespace after colons in dictionaries
        content = re.sub(r':([^=])', r': \1', content)
        
        # Fix multiple spaces before operators
        content = re.sub(r' +([+\-*/=<>!&|])', r' \1', content)
        
        # Fix E713 issues (not in instead of not ... in)
        content = re.sub(r'not (\w+) in (\w+)', r'\1 not in \2', content)
        
        # Fix E128 continuation line under-indented
        content = re.sub(r'(\s+)(\w+):\s*$', r'\1\2:', content, flags=re.MULTILINE)
        
        # Fix E231 missing whitespace after colon in function calls
        content = re.sub(r'(\w+):([^=])', r'\1: \2', content)
        
        # Fix E261 inline comments (at least two spaces)
        content = re.sub(r'([^ ]) +#', r'\1  #', content)
        
        # Fix E722 bare except
        content = re.sub(r'except:', r'except Exception:', content)
        
        # Fix E701 multiple statements on one line
        content = re.sub(r'([^:]) :([^:])', r'\1:\n    \2', content)
        
        # Fix W504 line break after binary operator
        content = re.sub(r'([+\-*/=<>!&|])\s*\n\s*', r'\1 ', content)
        
        # Fix E131 continuation line unaligned
        content = re.sub(r'(\s+)(\w+,\s*$)', r'\1\2', content, flags=re.MULTILINE)
        
        # Remove unused imports (basic cleanup)
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Skip unused imports (basic detection)
            if re.match(r'^from \.\.core\.models import .*Node.*Edge', line):
                if 'Node' not in content or 'Edge' not in content:
                    continue
            elif re.match(r'^import .*', line) and 'typing' in line:
                if 'typing' not in content[content.find(line) + len(line):]:
                    continue
                    
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Ensure file ends with newline
        if content and not content.endswith('\n'):
            content += '\n'
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix linting issues across the codebase."""
    src_dir = Path("src/network_ui")
    
    if not src_dir.exists():
        print("Source directory not found!")
        return
    
    fixed_count = 0
    total_files = 0
    
    for py_file in src_dir.rglob("*.py"):
        total_files += 1
        if fix_file(py_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} out of {total_files} files")

if __name__ == "__main__":
    main() 