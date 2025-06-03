import os
from pathlib import Path
import sys
sys.path.insert(0, os.path.abspath('../src/worldnavigator'))
sys.path.append(str(Path('./source/ext').resolve()))

project = 'WorldNavigator'
copyright = '2025, IkarosKurtz'
author = 'IkarosKurtz'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.coverage',
  'sphinx.ext.napoleon',
  'sphinx_copybutton',
  'renpydoc'
  # 'autoapi.extension'
]

# autoapi_type = 'python'
# autoapi_dirs = ['../src/worldnavigator']
# autoapi_ignore = ["__init__.py"]

# Make sure the master doc is 'index'
master_doc = 'index'

# Root directory for documentation
source_dir = '.'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_css_files = ['custom.css']
autoclass_content = "both"
