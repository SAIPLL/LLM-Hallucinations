import json
import argparse
from json_function_to_grammar import get_grammar

def get_schema(url):
	"""
		Returns schema with grammar
		url: path to read (json schema function) to create the grammar
	"""
	with open(url) as f:
		schema = json.load(f)
	return get_grammar(url=url, schema=schema)

def save_gbnf_grammar_from_documentation(lst_function=[], baseline_grammar='function.gbnf',grammar_name='question1.txt'):
	"""
		lst_function: List[str] list of paths to functions in json format
		baseline_grammar: file containing the base grammar from which to append the grammar
			from the functions
	"""
	if len(lst_function) > 0:
		# Read the baseline grammar file 
	    with open(baseline_grammar, 'r') as original_file:
	        original_lines = original_file.readlines()
	    
	    # Write the original lines to the new file (copy)
	    # Create name for file
	    copy_file_path = grammar_name.split('.')[0]+'-grammar.gbnf'
	    with open(copy_file_path, 'w') as copy_file:
	        copy_file.writelines(original_lines)
	    
	    # Get first Schema
	    schema_global = get_schema(lst_function[0])
	    for i in range(1, len(lst_function)):
	    	# Add following rules of functions
	    	schema = get_schema(lst_function[i])
	    	schema_global.merge_converter(schema)

	    # Append new grammar lines from the listed functions
	    with open(copy_file_path, 'a') as copy_file:
	    	copy_file.write('\n' + schema_global.format_grammar())
	else:
		print(f"No functions to add to baseline: {baseline_grammar}.")


if __name__ == '__main__':
	""" Write a grammar from a list of jsons' paths containing documentation """
	""" Example usage: python write_grammar.py --lst-function='question1.txt' --baseline-grammar='function.gbnf'"""
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--lst-function", help="File containing the list of json functions to add.")
	parser.add_argument("--baseline-grammar", help="File contaning the first lines of the baseline grammar.")

	args = parser.parse_args()
	# Read lines/functions in file
	if args.lst_function:
		with open(args.lst_function, 'r') as file:
			lst_function = file.readlines()
	lst_function = [file.strip() for file in lst_function]
	# Read baseline grammar file
	if args.baseline_grammar:
		baseline_grammar = args.baseline_grammar
	save_gbnf_grammar_from_documentation(lst_function, baseline_grammar, args.lst_function)