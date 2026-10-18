"""
  This is script that generates the grammars 
  for odex.
"""

import os
import re
import json
from module_to_schema import convert_data_to_schema
from write_grammar import save_gbnf_grammar_from_documentation


def add_library_alias(code_line, lib_alias):
  """
    Creates a dictionary with {name: alias}
    pairs, if alias is not found keep {name : name}
  """
  library = ""
  pattern = r"import\s+(\w+)\s+as\s+(\w+)"
  match = re.search(pattern, code_line)
  if match:
    library = match.group(1)
    alias = match.group(2)
    lib_alias[library] = alias
  else:
    pattern = r"from\s+(\w+)\s+import\s+(\w+)"
    match = re.search(pattern, code_line)
    if match:
      library = match.group(1)
      if library not in lib_alias:
        lib_alias[library] = library
    else:
      pattern = r"import\s+(\w+)"
      match = re.search(pattern, code_line)
      if match:
        library = match.group(1)
        if library not in lib_alias:
          lib_alias[library] = library
  return (lib_alias, library)

def create_libraries_doc(lib_lst, task_id, folder_name, lang):
  file_to_write = f"{folder_name}/{lang}_{str(task_id)}.txt"
  lib_write = []
  for lib in lib_lst:
    lib_write.append(f"{lib}/{lib}.txt\n")
  with open(file_to_write, "w") as f:
      f.write(''.join(lib_write))
  f.close()
  return file_to_write

def create_filter_doc(lib_lst, task_id, folder_name, lang):
  file_to_write = f"{folder_name}/filter_{lang}_{str(task_id)}.txt"
  filter_write = []
  pre_filter_libs = ["tensorflow", "scipy", "sklearn", "pytorch", "pandas", "numpy", "matplotlib"]
  for lib in lib_lst:
    if lib in pre_filter_libs:
      filter_write.append(f"{folder_name}/filter_{lib}.txt\n")
    else:
      filter_write.append("\n")
  with open(file_to_write, "w") as f:
      f.write(''.join(filter_write))
  f.close()
  return file_to_write

def main():
  lib_alias = dict()
  test_path = "../Library-Bench/odex/data"
  library_save = "Data/graph4code/output/odex"
  folder_name = 'files/odex'
  for filename in os.listdir(test_path):
    # Check if the file ends with '.jsonl'
    if filename.endswith('.jsonl'):
        # Construct the full file path
        full_path = os.path.join(test_path, filename)
        # Open the file
        with open(full_path, 'r', encoding='utf-8') as file:
          for line in file:
            # Load each line as a JSON object
            task_info = json.loads(line.strip())
            par_lib = []
            if "test_start" not in task_info:
              continue
            if "import " not in task_info["test_start"]:
              continue 
            # Get library needed
            for code_line in task_info["test_start"].split('\n'):
              lib_alias, another_lib = add_library_alias(code_line, lib_alias)
              if another_lib != "":
                par_lib.append(another_lib)
            # Perform JSON to JSON Schema
            library_task = task_info["library"]
            if "matplotlib" in library_task:
              library_task.append("matplotlib.pyplot")
            if "http" in library_task:
              library_task = ["http.server", "http.client"]
            if "urllib" in library_task:
              library_task = ["urllib", "urllib.parse", "urllib.request"]
            if "mpl_toolkits" in library_task:
              library_task.append("mpl_toolkits.mplot3d")
            library_task = [lib.replace('_','-') for lib in library_task]
            for i in range(0, len(library_task)):
              if library_task[i] == "aspose":
                library_task[i] = "aspose.words"
              # Convert if it has not been converted before
              # Get the current directory
              current_directory = os.getcwd()
              # Create the full path of the folder
              folder_path = os.path.join(current_directory, library_task[i])
              if not os.path.isdir(folder_path):
                try:
                  convert_data_to_schema(library_task[i], f"{library_save}/{library_task[i]}/{library_task[i]}.json", True)
                except:
                  convert_data_to_schema(library_task[i].replace('_','-'), f"{library_save.replace('_','-')}/{library_task[i].replace('_','-')}/{library_task[i].replace('_','-')}.json", True)
            # Get task_id to save the grammar for this question
            task_id = task_info["task_id"]
            library_task = [lib.replace('_','-') for lib in library_task]
            # Create lst_function
            #if "mpl-toolkits" in library_task:
            file_lib = create_libraries_doc(library_task, task_id, folder_name, filename[:2])
            # Get alias list
            alias_lst = [lib_alias[l] if l in lib_alias else l for l in library_task]
            alias_lst = [a if a != "matplotlib.pyplot" else "plt" for a in alias_lst]
            alias_lst = [a if a != "aspose.words" else "aw" for a in alias_lst]
            # Create lst_namespace
            #if "sympy" in library_task:
            file_filter = create_filter_doc(library_task, task_id, folder_name, filename[:2])
            #if "sympy" in library_task:
            save_gbnf_grammar_from_documentation('grammar/atomimport.gbnf', file_lib, alias_lst, library_task, file_filter)

if __name__ == '__main__':
  main()