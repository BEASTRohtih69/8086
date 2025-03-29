#!/usr/bin/env python3
import re

# Read the file
with open('instructions.py', 'r') as f:
    content = f.read()

# Fix all occurrences of the pattern
pattern = r'self\._get_register_by_index\((.*?)\)\(\)'
replacement = r'self._get_register_by_index(\1)'
content = re.sub(pattern, replacement, content)

# Write the file back
with open('instructions.py', 'w') as f:
    f.write(content)

print("Fixed all occurrences of the pattern in instructions.py")