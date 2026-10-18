"""
  This is script that generates the grammars 
  for BigCodeBench.
"""

import os
import re
import json
from module_to_schema import convert_data_to_schema
from write_grammar import save_gbnf_grammar_from_documentation

def create_JSON_schemas():
  # Get the current directory
  library_save = "../Data/graph4code/output/odex"
  # Create schemas for files in library save (Inspected libraries JSONs)
  time_file = 'time_json_schema.json'
  error_files = 'error_schema.json'
  json_time_lst = []
  error_schema_lst = []
  lst = ['ssl']
  #for fname in os.listdir(library_save):
  for fname in lst:
    path = os.path.join(library_save, fname, fname)
    path_json = f'{path}.json'
    folder_path = os.path.join('../', fname)
    if os.path.isfile(path_json):
      # Check if already we have the schema, if not create
      # from JSON in bigcodebench
      if not os.path.isdir(folder_path):
        try: 
          time_taken = convert_data_to_schema(fname.replace('_','-'), path_json, True)
          json_time_lst.append({'file': path_json, 'time': time_taken})
        except:
          error_schema_lst.append({'file':path_json, 'name': fname})
  #with open(time_file, 'w') as f:
    #json.dump(json_time_lst, f)
  #f.close()
  #with open(error_files, 'w') as f2:
    #json.dump(error_schema_lst, f2)
  #f2.close()

def create_libraries_doc(lib_lst, task_id, folder_name):
  file_to_write = f"{folder_name}/{str(task_id)}.txt"
  lib_write = []
  for lib in lib_lst:
    lib_write.append(f"{lib}/{lib}.txt\n")
  with open(file_to_write, "w") as f:
      f.write(''.join(lib_write))
  f.close()
  return file_to_write

def create_filter_doc(lib_lst, task_id, folder_name):
  file_to_write = f"{folder_name}/filter_{str(task_id)}.txt"
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

def create_grammars(from_id=0, library_filter=""):
  folder_name = 'files/bigcodebench'
  mapping_file = '../Library-Bench/bigcodebench/bigcodebench_mapping.json'
  alias_mapping_file = '../Library-Bench/bigcodebench/bigcodebench_alias_mapping.json'
  all_libraries_file = '../Library-Bench/bigcodebench/all_libraries.txt'

  rules_to_add = {
    'matplotlib': ['matplotlib-matplotlib-matplotlib-figure-figure-tight-layout ::= ""',
    'plt-plt-matplotlib-pyplot-figure-tight-layout ::= ""',
    'matplotlib-matplotlib-matplotlib-pylab-figure-tight-layout ::= ""'],
    'nltk': ['nltk-nltk-nltk-chunk-regexp-regexpparser-grammar ::= op-expr',
    'nltk-nltk-nltk-regexpparser-grammar ::= op-expr'],
    'urllib': ['urllib-error-urllib-request-openerdirector-error ::= ""',
    'urllib-parse-urllib-robotparser-robotfileparser-parse ::= "parse"']
  }
  rules_to_add_lib = []
  # Load the file containing the mappings of libraries
  with open(mapping_file, "r") as f:
    mappings = json.load(f)
  f.close()
  # Load file containing the alias
  with open(alias_mapping_file, "r") as f2:
    alias_mappings = json.load(f2)
  f2.close()
  with open(all_libraries_file, "r") as f3:
    all_libraries = f3.readlines()
  f3.close()
  # For each mapping construct a grammar
  for k, v in mappings.items():
    library = k.replace('_','-').split(',')
    task_id = v['id']
    is_library = (library_filter == "") or (library_filter in library)
    if task_id >= from_id and is_library:
      # collect matches
      matches = [k.strip() if k.startswith(f'{l}.') else l for k in all_libraries for l in library]
      # combine and remove duplicates
      library_task = list(set(library + matches))
      # Create lst_function
      file_lib = create_libraries_doc(library_task, task_id, folder_name)
      # Create lst_namespace
      file_filter = create_filter_doc(library_task, task_id, folder_name)
      alias_lst = [alias_mappings[l] if l in alias_mappings else l for l in library_task]
      #if "os.path" in alias_lst:
        #alias_lst.remove("os.path")
      #if "os.path" in library_task:
        #library_task.remove("os.path")
      #if "http" in alias_lst:
        #alias_lst.remove("http")
      #if "http" in library_task:
        #library_task.remove("http")
      #print(library_task)
      #print(task_id)
      for lib in library_task:
        if lib in rules_to_add:
          rules_to_add_lib += rules_to_add[lib]
      rules_to_add_lib = list(set(rules_to_add_lib))
      save_gbnf_grammar_from_documentation('grammar/atomimport.gbnf', file_lib, alias_lst, library_task, file_filter, rules_to_add=rules_to_add_lib, name_alias=True)

def main():
  #create_JSON_schemas()
  #create_grammars(0, library_filter="matplotlib")
  create_grammars(456, library_filter='')
  #create_grammars(0, library_filter='urllib')
  #create_grammars(0, library_filter='os')
  #create_grammars(0, library_filter='http')

if __name__ == '__main__':
  main()