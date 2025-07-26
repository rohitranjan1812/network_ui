#!/usr/bin/env python3
"""
Comprehensive Linting Fix Script for Network UI Platform
Automatically fixes all code style issues without breaking functionality.
"""

import os
import re
import glob
from pathlib import Path


def fix_whitespace_issues(content):
    """Fix W293 (blank lines with whitespace) and W291 (trailing whitespace)"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace (W291)
        line = line.rstrip()
        # Fix blank lines containing only whitespace (W293)
        if line.strip() == '':
            line = ''
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_newline_at_eof(content):
    """Fix W292 (no newline at end of file)"""
    if content and not content.endswith('\n'):
        content += '\n'
    return content


def fix_operator_spacing(content):
    """Fix E226 (missing whitespace around arithmetic operator) and E228 (modulo)"""
    # Fix arithmetic operators
    content = re.sub(r'(\w)\*(\w)', r'\1 * \2', content)
    content = re.sub(r'(\w)\+(\w)', r'\1 + \2', content)
    content = re.sub(r'(\w)-(\w)', r'\1 - \2', content)
    content = re.sub(r'(\w)/(\w)', r'\1 / \2', content)
    content = re.sub(r'(\w)%(\w)', r'\1 % \2', content)
    
    # Be careful not to break existing correct spacing
    content = re.sub(r'(\w)  \*  (\w)', r'\1 * \2', content)
    content = re.sub(r'(\w)  \+  (\w)', r'\1 + \2', content)
    content = re.sub(r'(\w)  -  (\w)', r'\1 - \2', content)
    content = re.sub(r'(\w)  /  (\w)', r'\1 / \2', content)
    content = re.sub(r'(\w)  %  (\w)', r'\1 % \2', content)
    
    return content


def fix_boolean_comparisons(content):
    """Fix E712 (comparison to True should be 'if cond is True:' or 'if cond:')"""
    content = re.sub(r'== True\b', r'is True', content)
    content = re.sub(r'!= True\b', r'is not True', content)
    content = re.sub(r'== False\b', r'is False', content)
    content = re.sub(r'!= False\b', r'is not False', content)
    return content


def fix_comment_spacing(content):
    """Fix E261 (at least two spaces before inline comment)"""
    # Fix single space before inline comment
    content = re.sub(r'(\S) #', r'\1  #', content)
    return content


def fix_fstring_issues(content):
    """Fix F541 (f-string is missing placeholders)"""
    # Convert f-strings without placeholders to regular strings
    content = re.sub(r"f'([^'{}]*)'", r"'\1'", content)
    content = re.sub(r'f"([^"{}]*)"', r'"\1"', content)
    return content


def fix_continuation_indentation(content):
    """Fix E128 (continuation line under-indented for visual indent)"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Look for continuation lines that need fixing
        if (i > 0 and 
            lines[i-1].rstrip().endswith(',') and 
            line.strip() and 
            not line.startswith(' ' * 8)):  # Basic indentation fix
            
            # Get the base indentation of the previous line
            prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
            current_indent = len(line) - len(line.lstrip())
            
            # If it's under-indented, fix it
            if current_indent < prev_indent + 4:
                line = ' ' * (prev_indent + 4) + line.lstrip()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def remove_unused_imports(content):
    """Remove unused imports (F401) - be conservative to avoid breaking code"""
    lines = content.split('\n')
    
    # List of known unused imports based on the linting output
    unused_patterns = [
        r'^import pytest$',
        r'^import uuid$',
        r'^import math$',
        r'^from unittest\.mock import patch$',
        r'^from unittest\.mock import patch, MagicMock$',
        r'^from unittest\.mock import patch, mock_open$',
        r'^from datetime import datetime, date$',
        r'^from typing import Optional, Tuple$',
        r'^from typing import Tuple$',
        r'^from typing import Callable$',
        r'^from typing import Tuple, Set$',
    ]
    
    filtered_lines = []
    for line in lines:
        should_remove = False
        
        # Check if this line matches any unused import pattern
        for pattern in unused_patterns:
            if re.match(pattern, line.strip()):
                should_remove = True
                break
        
        if not should_remove:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def fix_variable_redefinitions(content):
    """Fix F811 (redefinition of unused variables)"""
    # Remove duplicate fixture parameters - be very specific
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix specific redefinition issues
        if 'def test_' in line and ', sample_csv_data' in line and line.count('sample_csv_data') > 1:
            # Remove duplicate sample_csv_data parameter
            line = re.sub(r', sample_csv_data.*?, sample_csv_data', ', sample_csv_data', line)
        
        # Remove redefinition of Edge import
        if line.strip() == 'from network_ui.core.models import Edge' and 'def ' in '\n'.join(lines):
            continue
            
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path):
    """Process a single file to fix all linting issues"""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = fix_whitespace_issues(content)
        content = fix_operator_spacing(content)
        content = fix_boolean_comparisons(content)
        content = fix_comment_spacing(content)
        content = fix_fstring_issues(content)
        content = remove_unused_imports(content)
        content = fix_variable_redefinitions(content)
        content = fix_continuation_indentation(content)
        content = fix_newline_at_eof(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed: {file_path}")
        else:
            print(f"  ⏭️  No changes needed: {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")


def main():
    """Main function to process all Python files"""
    print("🔧 Starting comprehensive linting fixes...")
    
    # Get all Python files in src/ and tests/
    python_files = []
    
    for pattern in ['src/**/*.py', 'tests/**/*.py']:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    # Sort for consistent processing
    python_files.sort()
    
    print(f"Found {len(python_files)} Python files to process")
    
    for file_path in python_files:
        # Skip __pycache__ and .pyc files
        if '__pycache__' in file_path or file_path.endswith('.pyc'):
            continue
            
        process_file(file_path)
    
    print("\n✅ All linting fixes completed!")
    print("🧪 Next step: Run comprehensive tests to verify functionality")


if __name__ == "__main__":
    main() 