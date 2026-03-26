#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Save file as UTF-8 with BOM"""

import codecs

# Read the file
with open('setup_build.nsi', 'r', encoding='utf-8') as f:
    content = f.read()

# Write back with UTF-8 BOM
with codecs.open('setup_build_utf8.nsi', 'w', 'utf-8-sig') as f:
    f.write(content)

print("File saved as UTF-8 with BOM: setup_build_utf8.nsi")
