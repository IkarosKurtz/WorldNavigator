from collections import defaultdict, deque
import os
import re

original_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(original_path, 'src', 'worldnavigator')

exclude = [
  '__init__.py',
  'py.typed',
  '__pycache__',
]

# List project directories, excluding unwanted files/folders
dirs = [
  folder
  for folder in os.listdir(path)
  if folder not in exclude
]

# Collect all file paths
file_paths = []
for folder in dirs:
  files = [
    f
    for f in os.listdir(os.path.join(path, folder))
    if f not in exclude
  ]
  file_paths.extend(os.path.join(path, folder, f) for f in files)

# Count total lines of code (non-empty lines)
lines_of_code = 0
for file in file_paths:
  with open(file, 'r') as f:
    lines = f.readlines()
    for line in lines:
      if line.strip():
        lines_of_code += 1

print(f'Total files: {len(file_paths)}')
print(f'Total lines of code: {lines_of_code}')


def module_from_path(path, base_path):
  rel_path = os.path.relpath(path, base_path)
  # Convert file path to module name: replace path separators by dots and remove .py extension
  module = rel_path.replace(os.sep, '.')
  if module.endswith('.py'):
    module = module[:-3]
  return module


base_path = os.path.join(original_path, 'src')  # Adjust this according to your project structure

# Map module name -> file path
module_to_file = {}
for file in file_paths:
  module = module_from_path(file, base_path)
  module_to_file[module] = file

# Build dependency graph
dependencies = defaultdict(set)
dependents = defaultdict(set)

for file in file_paths:
  with open(file, 'r') as f:
    content = f.read()

  # Extract imported modules using regex (both 'import' and 'from' statements)
  # Examples matched:
  # import worldnavigator.types.types
  # from worldnavigator.types.types import BaseCondition
  imports = re.findall(r'^\s*(?:from|import)\s+([\w\.]+)', content, re.MULTILINE)

  for imported_module in imports:
    # If the imported module or any of its prefixes is in module_to_file, consider it a dependency
    # For example, if you import 'worldnavigator.types.types', detect that file
    # Also detect more general imports (e.g. 'worldnavigator.types')
    parts = imported_module.split('.')
    for i in range(len(parts), 0, -1):
      prefix = '.'.join(parts[:i])
      if prefix in module_to_file:
        dependencies[file].add(module_to_file[prefix])
        dependents[module_to_file[prefix]].add(file)
        break  # Add only the most specific dependency found

# Topological sort using Kahn's algorithm
queue = deque([f for f in file_paths if not dependencies[f]])
sorted_files = []

while queue:
  current = queue.popleft()
  sorted_files.append(current)
  for dependent in dependents[current]:
    dependencies[dependent].remove(current)
    if not dependencies[dependent]:
      queue.append(dependent)

if len(sorted_files) != len(file_paths):
  raise Exception("Cyclic dependency detected")

print('\n'.join(sorted_files))


# Helper function to normalize import lines by removing extra spaces
def normalize_import(line):
  return re.sub(r"\s+", " ", line.strip())


# Dictionaries to store import statements
imports_dict = defaultdict(set)
direct_imports = set()

# Create the final .rpy file path
new_rpy_path = os.path.join(original_path, 'worldnavigator.rpy')

with open(new_rpy_path, 'w') as f:
  f.write('init -999 python:\n')

  # Collect all imports and clean code content
  file_contents = []

  for file in sorted_files:
    parent_folder, file_name = file.split('\\')[-2:]
    with open(file, 'r') as cf:
      content = cf.read()

      content_lines = []
      for line in content.splitlines():
        stripped = line.strip()
        # Skip lines inside TYPE_CHECKING blocks
        if stripped.startswith('if TYPE_CHECKING'):
          continue

        # Process import statements
        if stripped.startswith('import ') or stripped.startswith('from '):
          norm_line = normalize_import(stripped)
          # Skip imports from 'worldnavigator' modules (they will be handled globally)
          if "worldnavigator" in norm_line:
            continue

          if norm_line.startswith("import "):
            modules = [mod.strip() for mod in norm_line.replace("import ", "").split(",")]
            for mod in modules:
              if mod not in direct_imports:
                direct_imports.add(mod)

          elif norm_line.startswith("from "):
            match = re.match(r"from ([\w\.]+) import (.+)", norm_line)
            if match:
              module, names = match.groups()
              names_set = set([name.strip() for name in names.split(",")])
              imports_dict[module].update(names_set)
        else:
          # Non-import code lines are collected
          content_lines.append(line)

      content_body = '\n'.join(content_lines)
      file_contents.append((
        parent_folder, file_name, content_body
      ))

  # Write unified imports at the top of the .rpy file
  for mod in sorted(direct_imports):
    f.write(f'  import {mod}\n')

  for module, names in sorted(imports_dict.items()):
    names_str = ", ".join(sorted(names))
    f.write(f'  from {module} import {names_str}\n')

  # Write the content of each file in order
  for parent_folder, file_name, content_body in file_contents:
    f.write(f'  # =====================================================================\n')
    f.write(f'  # {parent_folder}/{file_name}\n')
    f.write(f'  # =====================================================================\n\n')
    f.write('  ' + content_body.replace('\n', '\n  '))
    f.write('\n')
