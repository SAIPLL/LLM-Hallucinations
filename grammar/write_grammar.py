import argparse
import ast
import datetime
import json
import re
from json_function_to_grammar import get_grammar

def get_schema(url, alias, name):
	"""
		Returns schema with grammar
		url: path to read (json schema function) to create the grammar
	"""
	with open(url) as f:
		schema = json.load(f)
	return get_grammar(url=url, schema=schema, alias=alias, name=name)

def connect_library_rules(aliases=[]):
	"""
		Return grammar rules which connects classes and methods
	"""
	rules = []
	alias_format = [f'[^"{alias}."]' for alias in aliases]
	alias_builders = [f'{alias}-lib-builders' for alias in aliases]
	alias_methods = [f'{alias}-lib-methods' for alias in aliases]
	rules.append(
		"except-lib ::= " + " | ".join(alias_format) + "\n"
	)
	rules.append(
	    "library ::= " + "| ".join(alias_builders) + "\n"
	)
	rules.append(
	    "methods ::= name | " + "| ".join(alias_methods)
	)
	return rules

def run_write_schema(lst_function, alias, name, file_path):
	"""
		Processes and writes the grammar into a file
	"""
	start_time = datetime.datetime.now()
	
	# Read lines/functions in file
	with open(lst_function, 'r') as file:
		lst_function = file.readlines()
	
	# Sort lines, prioritizing those containing '__init__'
	sorted_lines = sorted(lst_function, key=lambda line: (0 if '__init__' in line else 1, line))
	lst_function = [file.strip() for file in sorted_lines]
	# Get first Schema
	schema_global = get_schema(lst_function[0], alias, name)
	start_time = datetime.datetime.now()
	for i in range(1, len(lst_function)):
		# Add following rules of functions
		schema = get_schema(lst_function[i], alias, name)
		schema_global.merge_converter(schema)
		#print(f"Done ({i}): {lst_function[i]}")
	schema_global.format_lib(alias)
	schema_global._rules.pop('libmethods')
	schema_global._rules.pop('lib')

	# Append new grammar lines from the listed functions
	with open(file_path, 'a') as copy_file:
		copy_file.write('\n' + schema_global.format_grammar().replace('ExceptHandler','excepthandler'))

	end_time = datetime.datetime.now()
	print(f"# Rules: {len(lst_function)}, Duration (s): {(end_time-start_time).total_seconds()}")

def save_gbnf_grammar_from_documentation(baseline_grammar='function.gbnf',grammar_name='question1.txt', alias=['pd'], name=['pandas']):
	"""
		lst_function: List[str] list of paths to functions in json format
		baseline_grammar: file containing the base grammar from which to append the grammar
			from the functions
		grammar_name: contains a list of the file_paths of the library to use
	"""
	# Read list of libraries to use
	with open(grammar_name, 'r') as file:
		lst_files = file.readlines()

	# Read the baseline grammar file 
	with open(baseline_grammar, 'r') as original_file:
		original_lines = original_file.readlines()

	# Write the original lines to the new file (copy)
	# Create name for file
	match = re.search(r'/([^/.]+)\.', baseline_grammar)
	name_of_grammar = match.group(1)
	copy_file_path = 'grammar/'+grammar_name[:-4]+'-'+name_of_grammar+'-grammar.gbnf'
	with open(copy_file_path, 'w') as copy_file:
		copy_file.writelines(original_lines)
	
	for i in range(0, len(alias)):
		run_write_schema(lst_files[i].strip(), alias[i], name[i], copy_file_path)

	# Add the two lines to connect the library grammar
	c_rules = connect_library_rules(alias)
	with open(copy_file_path, 'a') as copy_file:
		copy_file.writelines(c_rules)

# Define a custom argument type for a list of strings
def list_of_strings(arg):
    return ast.literal_eval(arg)

if __name__ == '__main__':
	""" Write a grammar from a list of jsons' paths containing documentation """
	""" Example usage: python write_grammar.py --lst-function='pandas/pandas.txt' --baseline-grammar='any.gbnf' --alias='pd'"""
	""" Example usage: python write_grammar.py --lst-function='numpy/numpy.txt' --baseline-grammar='any.gbnf' --alias='np' """
	""" Example usage: python write_grammar.py --lst-function='matplotlib.pyplot.txt' --baseline-grammar='any.gbnf' --alias=['plt'] --name=['matplotlib.pyplot'] """
	
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--lst-function", help="File containing the list of json functions to add.")
	parser.add_argument("--baseline-grammar", help="File contaning the first lines of the baseline grammar.")
	parser.add_argument("--alias", help="List of most common library's alias to prefix rule.", type=list_of_strings)
	parser.add_argument("--name", help="List of libraries name.", type=list_of_strings)


	args = parser.parse_args()
	save_gbnf_grammar_from_documentation(args.baseline_grammar, args.lst_function, args.alias, args.name)

	#save_gbnf_grammar_from_documentation("any.gbnf", "numpy.txt", ['np'], ["numpy"])


