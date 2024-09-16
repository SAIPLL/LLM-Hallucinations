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

def negate_alias_name(aliases=[], names=[], rules=[]):
	"""
		Negates an alias correctly and adds these
		rules to the connection rules
	"""

	# Add negation of module name
	for name in names:
		rules.append(
			f'non-{name}-name ::= ( \"{name}\" [^.] ) \n'
		)
	# Add correct negation of alias
	for alias in aliases:
		non_alias_rule = []
		alias_dot = alias + "."
		for i in range(1, len(alias_dot) + 1):
			alias_format = f' \"{alias_dot[:i-1]}\" [^{alias_dot[i-1:i]}] '
			non_alias_rule.append(alias_format)	
		rules.append(
			f'non-{alias} ::= ( ' + " | ".join(non_alias_rule) + " ) \n"
		)

	return rules

def connect_library_rules(aliases=[], names=[], original_name=[]):
	"""
		Return grammar rules which connects classes and methods
	"""
	rules = []
	alias_format = [f'non-{alias}' for alias in aliases]
	name_format = [f'non-{name}-name' for name in original_name]
	alias_inits = [f'{alias}-lib-inits' for alias in aliases]
	name_builtins = [f'{name}-lib-builtins' for name in names]
	without_alias_inits = [f'{alias}-lib-inits-none' for alias in aliases]
	whithout_name_builtins = [f'{name}-lib-builtins-none' for name in names]
	rules.append(
		("except-lib ::= ( " + " | ".join(alias_format) + ' | ' +  " | ".join(name_format) + " ) \n")
	)
	rules.append(
	    ("library ::= ( " + " | ".join(alias_inits) + ' | ' + " | ".join(name_builtins) + ' | ' + " | ".join(without_alias_inits) + ' | ' + " | ".join(whithout_name_builtins) + " ) \n")
	)
	rules = negate_alias_name(aliases, original_name, rules)
	return rules

def belongs_list(file_function, lst_filter):
	"""
		Returns a boolean if the file is in the filter list
	"""
	for f in lst_filter:
		if f in file_function:
			return True
	return False

def run_write_schema(lst_function, alias, name, file_path, lst_filter):
	"""
		Processes and writes the grammar into a file
	"""
	start_time = datetime.datetime.now()
	
	# Read lines/functions in file
	with open(lst_function, 'r') as file:
		lst_function = file.readlines()

	# Read lines of modules to filter from files
	with open(lst_filter, 'r') as ff:
		lst_filter = ff.readlines()

	# Sort lines, prioritizing those containing '__init__'
	sorted_lines = sorted(lst_function, key=lambda line: (0 if '__init__' in line else 1, line))
	lst_function = [file.strip() for file in sorted_lines]
	lst_filter = [file.strip() for file in lst_filter]
	# Get first Schema)
	start_time = datetime.datetime.now()
	schema_global = get_schema(lst_function[0], alias, name)
	for i in range(1, len(lst_function)):
		# Add following rules of functions
		if lst_function[i].endswith(".json"):
			if belongs_list(lst_function[i], lst_filter):
				schema = get_schema(lst_function[i], alias, name)
				schema_global.merge_converter(schema)
		#print(f"Done ({i}): {lst_function[i]}")
	schema_global.format_lib(alias)
	if 'lib-builtins' in schema_global._rules:
		schema_global._rules.pop('lib-builtins')
	schema_global._rules.pop('lib-inits')

	# Append new grammar lines from the listed functions
	with open(file_path, 'a') as copy_file:
		copy_file.write('\n' + schema_global.format_grammar().replace('ExceptHandler','excepthandler'))

	end_time = datetime.datetime.now()
	print(f"# Rules: {len(lst_function)}, Duration (s): {(end_time-start_time).total_seconds()}")

def save_gbnf_grammar_from_documentation(baseline_grammar='function.gbnf',modules_list='question1.txt', alias=['pd'], name=['pandas'], namespace_filter=""):
	"""
		lst_function: List[str] list of paths to functions in json format
		baseline_grammar: file containing the base grammar from which to append the grammar
			from the functions
		grammar_name: contains a list of the file_paths of the library to use
	"""
	# Read list of libraries to use
	with open(modules_list, 'r') as file:
		lst_files = file.readlines()

	# Read list of filters to use
	with open(namespace_filter, 'r') as file_filter:
		lst_filters = file_filter.readlines()

	# Read the baseline grammar file 
	with open(baseline_grammar, 'r') as original_file:
		original_lines = original_file.readlines()

	# Write the original lines to the new file (copy)
	# Create name for file
	match = re.search(r'/([^/.]+)\.', baseline_grammar)
	name_of_grammar = match.group(1)
	copy_file_path = 'grammar/'+modules_list[:-4]+'-'+name_of_grammar+'-grammar.gbnf'
	with open(copy_file_path, 'w') as copy_file:
		copy_file.writelines(original_lines)
	
	for i in range(0, len(alias)):
		run_write_schema(lst_files[i].strip(), alias[i], name[i], copy_file_path, lst_filters[i].strip())

	# Add the two lines to connect the library grammar
	# If any name contains '.' change it to '-'
	names = [n.replace('.','-') for n in name]
	c_rules = connect_library_rules(alias, names, name)
	with open(copy_file_path, 'a') as copy_file:
		copy_file.writelines(c_rules)

# Define a custom argument type for a list of strings
def list_of_strings(arg):
    return ast.literal_eval(arg)

if __name__ == '__main__':
	""" Write a grammar from a list of jsons' paths containing documentation """
	""" Example usage: python write_grammar.py --lst-function='matplotlib.pyplot.txt' --baseline-grammar='any.gbnf' --alias="['plt']" --name="['matplotlib.pyplot']" """
	""" Example usage: python grammar/write_grammar.py --lst-function='ds.txt' --baseline-grammar='grammar/any.gbnf' --alias="['pd','np','sklearn','scipy','torch','tf','plt']" --name="['pandas','numpy','sklearn','scipy','torch','tensorflow','matplotlib.pyplot']" """
	""" Example usage: python grammar/write_grammar.py --lst-function='numpy.txt' --baseline-grammar='grammar/generic.gbnf' --alias="['np']" --name="['numpy']" --lst-namespace='filter_numpy.txt' """
	""" Example usage: python grammar/write_grammar.py --lst-function='numpy_pandas.txt' --baseline-grammar='grammar/any.gbnf' --alias="['np','pd']" --name="['numpy','pandas']" --lst-namespace='filter.txt' """
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--lst-function", help="File containing the list of json functions to add.")
	parser.add_argument("--baseline-grammar", help="File contaning the first lines of the baseline grammar.")
	parser.add_argument("--alias", help="List of most common library's alias to prefix rule.", type=list_of_strings)
	parser.add_argument("--name", help="List of libraries name.", type=list_of_strings)
	parser.add_argument("--lst-namespace", help="File containing a list of modules to filter.")


	args = parser.parse_args()
	save_gbnf_grammar_from_documentation(args.baseline_grammar, args.lst_function, args.alias, args.name, args.lst_namespace)

	#save_gbnf_grammar_from_documentation("any.gbnf", "numpy.txt", ['np'], ["numpy"])


