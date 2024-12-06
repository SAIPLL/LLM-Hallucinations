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

def negate_alias_name(alias="", name="", add_dot=False):
	"""
		Negates an alias correctly and adds these
		rules to the connection rules
	"""
	words = alias + name
	dct_negations = {}
	for w in words:
		if add_dot:
			alias_dot = w + "."
		else: 
			alias_dot = w
		for i in range(1, len(alias_dot) + 1):
			l_rule = f'\"{alias_dot[:i-1]}\"'
			r_rule = f'{alias_dot[i-1:i]}'
			if l_rule not in dct_negations:
				dct_negations[l_rule] = set(r_rule)
			else:
				dct_negations[l_rule] = dct_negations[l_rule].union(set(r_rule))
	rule = "( "
	if not add_dot:
		dct_negations[f'""'] = dct_negations[f'""'].union(set([".","=",",","["," ","(",")","'","\"","{","}","+","-","&","*","@","/","%","^","|","<",">","#"]))
	for k,v in dct_negations.items():
		rule += f'{k} [^{"".join(v)}] | '
	rule = rule[:-3]
	rule += " )"
	return rule

def belongs_list(file_function, lst_filter):
	"""
		Returns a boolean if the file is in the filter list
	"""
	for f in lst_filter:
		if f in file_function:
			return True
	return False

def add_library_connector(name, rule, library_dict):
	"""
		Adds connector rules to library
	"""
	if name not in library_dict:
		library_dict[name] = {"library" : rule.replace('(  | ', '( ')}
	else:
		library_dict[name] = {"library" : f" ( {library_dict[name]['library']} | {rule} )".replace('(  | ', '( ')  }
	return library_dict

def read_file(file_name):
	"""
		Return lines of a file
	"""
	with open(file_name, 'r') as file:
		lines = file.readlines()
	file.close()
	return lines

def run_write_schema(lst_function, alias, name, file_path, lst_filter, library_dict):
	"""
		Processes and writes the grammar into a file
	"""
	start_time = datetime.datetime.now()
	
	# Read lines/functions in file
	lst_function = read_file(lst_function)
	# Sort lines, prioritizing those containing '__init__'
	sorted_lines = sorted(lst_function, key=lambda line: (0 if '__init__' in line else 1, line))
	lst_function = [file.strip() for file in sorted_lines]
	if len(lst_filter) > 1:
		# Read lines of modules to filter from files
		lst_filter = read_file(lst_filter)
		lst_filter = [file.strip() for file in lst_filter]
	else:
		# There is not a filter file, empty the filter list
		lst_filter = []
	
	# Get first Schema
	start_time = datetime.datetime.now()
	schema_global = get_schema(lst_function[0], alias, name)
	for i in range(1, len(lst_function)):
		# Add following rules of functions
		if lst_function[i].endswith(".json"):
			if len(lst_filter) > 0:
				if belongs_list(lst_function[i], lst_filter):
					schema = get_schema(lst_function[i], alias, name)
					schema_global.merge_converter(schema)
			else:
				schema = get_schema(lst_function[i], alias, name)
				schema_global.merge_converter(schema)
		#print(f"Done ({i}): {lst_function[i]}")
	
	# Adds alias and name to beginning of rules
	schema_global.format_lib()
	# Pop rules from global_schema and adds them to dictionary
	if 'lib-builtins' in schema_global._rules:
		#if name != "tensorflow":
		library_dict = add_library_connector(name, schema_global._rules["lib-builtins"], library_dict)
		schema_global._rules.pop('lib-builtins')
	if 'lib-inits' in schema_global._rules:
		library_dict = add_library_connector(name, schema_global._rules["lib-inits"], library_dict)
		schema_global._rules.pop('lib-inits')
	# Adds the root rule
	library_dict[name] = { 
		"library" : library_dict[name]['library']
	}

	# Append new grammar lines from the listed functions
	with open(file_path, 'a') as copy_file:
		#copy_file.write('\n' + schema_global.format_grammar().replace('ExceptHandler','excepthandler'))
		copy_file.write('\n' + schema_global.format_grammar())

	end_time = datetime.datetime.now()
	print(f"# Rules: {len(lst_function)}, Duration (s): {(end_time-start_time).total_seconds()}")
	return library_dict

def save_gbnf_grammar_from_documentation(baseline_grammar='function.gbnf',modules_list='question1.txt', alias=['pd'], name=['pandas'], namespace_filter=""):
	"""
		lst_function: List[str] list of paths to functions in json format
		baseline_grammar: file containing the base grammar from which to append the grammar
			from the functions
		grammar_name: contains a list of the file_paths of the library to use
	"""
	# Read list of libraries to use
	lst_files = read_file(modules_list)
	lst_filters = read_file(namespace_filter)
	original_lines = read_file(baseline_grammar)

	# Write the original lines to the new file (copy)
	# Create name for file
	match = re.search(r'/([^/.]+)\.', baseline_grammar)
	name_of_grammar = match.group(1)
	copy_file_path = 'grammar/'+modules_list[:-4]+'-'+name_of_grammar+'-grammar.gbnf'
	with open(copy_file_path, 'w') as copy_file:
		copy_file.writelines(original_lines)
	
	# Dictionary to save all library connector rules
	library_dict = {}
	for i in range(0, len(alias)):
		library_dict = run_write_schema(lst_files[i].strip(), alias[i], name[i], copy_file_path, lst_filters[i].strip(), library_dict)

	with open(copy_file_path, 'a') as copy_file:
		# Add connector rules to file
		library_rules = [library_dict[k]["library"] for k in library_dict.keys()]
		c_rules = []
		# Create negations
		c_rules.append(f"class-name ::= ( {negate_alias_name(alias, name, add_dot=False)} )+ \n")
		if len(library_rules) > 1:
			c_rules.append(f"library ::= ( {'|'.join(library_rules)} ) \n")
		else:
			c_rules.append(f"library ::= ( {library_rules[0]} ) \n")
		c_rules.append(f"root ::= ( {negate_alias_name(alias, name, add_dot=True)} | library )+ \n")

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
	""" Example usage: python grammar/write_grammar.py --lst-function='dsall.txt' --baseline-grammar='grammar/generic.gbnf' --alias="['np','pd']" --name="['numpy','pandas']" --lst-namespace='filter.txt' """
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--lst-function", help="File containing the list of json functions to add.")
	parser.add_argument("--baseline-grammar", help="File contaning the first lines of the baseline grammar.")
	parser.add_argument("--alias", help="List of most common library's alias to prefix rule.", type=list_of_strings)
	parser.add_argument("--name", help="List of libraries name.", type=list_of_strings)
	parser.add_argument("--alias-file", help="File containing the list of libraries aliases.") 
	parser.add_argument("--name-file", help="File containing the list of libraries names.") 
	parser.add_argument("--lst-namespace", help="File containing a list of modules to filter.")

	args = parser.parse_args()
	if args.alias_file:
		alias_lst = read_file(args.alias_file)
	else:
		alias_lst = args.alias
	if args.name_file:
		name_lst = read_file(args.name_file)
	else:
		name_lst = args.name

	save_gbnf_grammar_from_documentation(args.baseline_grammar, args.lst_function, alias_lst, name_lst, args.lst_namespace)

	#save_gbnf_grammar_from_documentation("any.gbnf", "numpy.txt", ['np'], ["numpy"])


