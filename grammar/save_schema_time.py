from module_to_schema import convert_data_to_schema
from write_grammar import save_gbnf_grammar_from_documentation
import os
import datetime

folder_name = 'Data/graph4code/output/modules_test'
file_output = 'schema_time_to_create.txt'
file_output = 'grammar_time_to_create_final.txt'
folder_name_output = 'files/test'

# Create schema lines
"""
for module in os.listdir(folder_name):
	with open(file_output, 'a') as f:
		try:
			file_name = f'{folder_name}/{module}/{module}.json'
			schema_time = convert_data_to_schema(module, file_name, True, True)
			f.write(f'Duration: {schema_time}, module: {module}\n')
		except:
			print(f'Mising {module}')
"""

# Create grammar

def create_libraries_doc(lib_lst, task_id=1, folder_name='', lang='en'):
  file_to_write = f"grammar/{folder_name}/{lang}_{str(task_id)}.txt"
  lib_write = []
  for lib in lib_lst:
    lib_write.append(f"{lib}/{lib}.txt\n")
    with open(file_to_write, "w") as f:
      f.write(''.join(lib_write))
  f.close()
  return file_to_write

def create_filter_doc(lib_lst, task_id=1, folder_name='', lang='en'):
  file_to_write = f"grammar/{folder_name}/filter_{lang}_{str(task_id)}.txt"
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


for module in os.listdir(folder_name):
	if '.DS_Store' in module:
		continue
	try:
		with open(file_output, 'a') as f:
			library_task = [module]
			start_time = datetime.datetime.now()
			file_lib = create_libraries_doc(library_task, folder_name=folder_name_output)
			alias_lst = [module]
			# Create lst_namespace
			#if "sympy" in library_task:
			file_filter = create_filter_doc(library_task, folder_name=folder_name_output)
			#if "sympy" in library_task:
			save_gbnf_grammar_from_documentation('grammar/atomimport.gbnf', file_lib, alias_lst, library_task, file_filter)
			end_time = datetime.datetime.now()
			duration_time = end_time-start_time
			f.write(f'Duration: {duration_time}, module: {module}\n')
	except:
		print(f'Module "{module}" not found')
