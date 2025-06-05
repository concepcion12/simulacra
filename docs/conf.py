import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Simulacra'
extensions = ['myst_parser']
source_suffix = ['.rst', '.md']
exclude_patterns = []
html_theme = 'alabaster'
templates_path = ['_templates']
html_static_path = ['_static']
