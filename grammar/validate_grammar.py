"""
	This script evaluates faithful code using the gbnf-validator
"""

import argparse
import json
import os
import re
import subprocess
import cProfile
import pstats
import concurrent.futures as cfuts
import time
from tqdm import tqdm


def remove_tmp_file(file_name):
	"""
	Delete temporal file to evaluate
	"""
	# Check if the file exists
	if os.path.exists(file_name):
	    # Delete the file
	    os.remove(file_name)
	    print(f"{file_name} has been deleted.")
	else:
	    print(f"{file_name} does not exist.")

def postprocess(code):
    if type(code) is list:
        code = code[0]
    code = code.split('</code>')[0]
    code = code.replace('```python', '')
    code = code.split('```')[0]
    code = code.split('\nEND SOLUTION')[0]
    code = code.replace('<code>', '')
    return code

def clean_code(code):
    # Define the pattern to match the first occurrence of any of the keywords
    pattern = r'.*?(?=(\bdef |\bimport |\bfrom ))'
    
    # Use regex to remove everything before the first match
    cleaned_code = re.sub(pattern, '', code, count=1, flags=re.DOTALL)
    
    return cleaned_code

def transform_to_one_line(code):
    lines = code.splitlines()  # Split code into individual lines
    result = []  # Store transformed lines
    buffer = []  # Temporary buffer to accumulate multi-line statements
    open_parentheses = 0  # Track open parentheses

    for line in lines:
        stripped_line = line.strip()  # Remove leading and trailing whitespace
        if not stripped_line:  # Skip empty lines
            continue
        if line.startswith("#"):
        	continue
        # Count parentheses to check if the statement is complete
        open_parentheses += stripped_line.count("(") - stripped_line.count(")")
        buffer.append(stripped_line)

        # If parentheses are balanced, finalize the current statement
        if open_parentheses == 0:
            result.append(" ".join(buffer))  # Join buffered lines into one
            buffer = []  # Reset buffer

    # Join all statements into a single string with proper formatting
    return "\n".join(result)

def write_str_file(file_model, code_info, library_name, is_answer, split_lines=False, test_name="DS"):
	"""
		Write the file into a string
	"""
	# Write code answer only
	if is_answer:
		if type(code_info['id']) == str:
			file_to_write = f"{file_model}_{code_info['id'].replace('/','-')}.py"
		else:
			file_to_write = f"{file_model}_{code_info['id']}.py"
		code = code_info["code"]
	else:
		file_to_write = f"{file_model}_{code_info['completion_id']}.py"
		code = code_info["generate_code"]
	
	if test_name != 'bigcodebench':
		extracted_code = postprocess(code)
		extracted_code = clean_code(extracted_code)
		extracted_code = re.sub(r'""".*?"""', '', extracted_code, flags=re.DOTALL)
	else:
		remove_sub = ':\n\n    pass'
		indx = code.find(remove_sub)
		if indx:
			indx = indx + len(remove_sub) + 1
			extracted_code = code[indx:]
		else:
			extracted_code = code
	
	if split_lines:
		extracted_code = transform_to_one_line(extracted_code)
		extracted_code += "\n"
		file_to_write_lst = []
		i = 0
		for line in extracted_code.split('\n'):
			if len(line) > 0:
				file_to_write = f"{file_to_write}_{i}"
				with open(file_to_write, "w") as f:
					f.write(line)
				f.close()
				file_to_write_lst.append(file_to_write)
				i += 1
		return file_to_write_lst
	else:
		extracted_code += "\n"
		with open(file_to_write, "w") as f:
			f.write(extracted_code)
		f.close()
		return [file_to_write]

def get_parse_result(output_str):
	"""
		String passes or not the generation
	"""
	result = ""
	lines = ""
	# Find error line
	error_index = output_str.find("Error:")
	parse_index = output_str.find("parse")
	print(output_str)
	if error_index > 0:
		# Find error substring
		error_line = output_str[error_index:]
		# Find end of line index
		eof_idx = error_line.find("\n")
		result = error_line[:eof_idx]
		if "Unexpected end of input" in result:
			result = "unexpected"
	elif parse_index > 0:
		result = "parse error"
	else:
		result = "pass"

	return result, output_str

def check_correctness(file_name, grammar, timeout=12000, sub_process=0):
	"""
		Executes the grammar validation of a program
		Timeout = 900
	"""

	# Path to the C++ binary
	binary_path = './llama-gbnf-validator'
	instruction = f'{binary_path} {grammar} {file_name}'
	time_taken = 0
	try:
		start = time.time()
		result_sub = subprocess.run([instruction], stdout=subprocess.PIPE, stderr=None, text=True, shell=True, timeout=timeout)
		output, lines = get_parse_result(result_sub.stdout)
		end = time.time()
		time_taken = end-start
	except subprocess.TimeoutExpired:
		# result_sub.kill()
		output = "timeout"
		lines = ""
	except:
		output = "char error"
		lines = ""

	return dict(
		passed=output,
		result=lines,
		completion_id=file_name,
		cid=sub_process,
		duration=time_taken
	)

def sequential_evaluate(code_file, model_name, is_answer, library="", test_name="DS", split_lines=False):
	"""
		Test generation on grammar in a sequential manner
	"""

	results_file = f"{model_name}_grammar_validation.jsonl"

	results = [json.loads(l) for l in open(code_file, "r")]
	validator_results = []
	# Profiling
	pr = cProfile.Profile()
	pr.enable()
	ix = 0
	for code_test in results:
		if test_name == 'bigcodebench':
			lib_col = 'libs'
		else:
			lib_col = 'library' 
		if is_answer:
			library_name = code_test['metadata'][lib_col]
		else:
			library_name = code_test[lib_col]
		if library_name == library or library == "":
			if test_name == "odex":
				grammar_name = f"files/odex/{code_test['lang']}_{code_test['id']}-atomimport-grammar.gbnf"
			else:
				grammar_name = f"files/{library_name.lower()}-atomimport-grammar.gbnf"
			file_names_lst = write_str_file(model_name, code_test, library_name, is_answer, split_lines=split_lines, test_name=test_name)
			for file_name in file_names_lst:
				response = check_correctness(file_name, grammar_name, timeout=12000)
				cid = response['completion_id']
				remove_tmp_file(cid)
				validator_results.append(response)
		ix = ix+1
	# Print profiling
	pr.disable()
	pr.print_stats(sort='tottime')

	with open(results_file, "w") as rf:
		for r in validator_results:
			rf.write(json.dumps(r) + '\n')

def find_grammar_odex(odex_mappings, library_name):
	lib_str = ','.join(sorted(library_name))
	for m in odex_mappings:
		if m["library"] == lib_str:
			return m["grammar"]
	return ""

def find_grammar_bigcodebench(bigcodebench_mappings, library_name):
	lib_str = library_name.replace('[','').replace(']','').replace(' ','').replace('\'','')
	lib_str = ','.join(sorted(lib_str.split(',')))
	if lib_str in bigcodebench_mappings:
		id = bigcodebench_mappings[lib_str]['id']
		file_grammar = f'files/bigcodebench/{id}-atomimport-grammar.gbnf'
		return file_grammar
	return ""

def find_example(odex_example, odex_id):
	for ex in odex_example:
		print(ex['id'], odex_id)
		if str(ex['id']) == str(odex_id):
			return ex['metadata']['library']

def evaluate_code_grammar(code_file, model_name, is_answer, library, test_name, split_lines=False):
	"""
		Compare output from generation to grammar
	"""
	
	results_file = f"{model_name}_grammar_validation.jsonl"

	results = [json.loads(l) for l in open(code_file, "r")]

	remove_files = []

	odex_mappings = [json.loads(l) for l in open("odex_grammar_mapping.jsonl", "r")]

	odex_example = [json.loads(l) for l in open("../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl", "r")]

	with open("bigcodebench_mapping.json", "r") as f:
		bigcodebench_mappings = json.load(f)
		f.close()

	#print(type(bigcodebench_mappings))
	validator_results = []
	with cfuts.ProcessPoolExecutor(
		max_workers=16
	) as executor:
		futs = []
		ix = 0
		for code_test in results:
			if test_name == 'bigcodebench':
				lib_col = 'libs'
			else:
				lib_col = 'library' 
			if is_answer:
				if test_name == 'odex' and model_name in ['gemma2-2b-0', 'qwen3-8b-0']:
					library_name = find_example(odex_example, code_test['id'])
				else:
					if test_name == 'bigcodebench' :
						library_name = json.loads(code_test['metadata'])[lib_col]
					else:
						library_name =  code_test['metadata'][lib_col]
			else:
				library_name = code_test[lib_col]
			
			if library_name == library or library == "":
				if test_name == "odex":
					grammar_name = find_grammar_odex(odex_mappings, library_name)
					print(grammar_name)
					#grammar_name = f"files/odex/{code_test['lang']}_{code_test['id']}-atomimport-grammar.gbnf"
				elif test_name == 'bigcodebench':
					grammar_name = find_grammar_bigcodebench(bigcodebench_mappings, library_name)
					print(grammar_name)
				else:
					grammar_name = f"files/{library_name.lower()}-atomimport-grammar.gbnf"
				file_names_lst = write_str_file(model_name, code_test, library_name, is_answer, split_lines=split_lines, test_name=test_name)
				
				for file_name in file_names_lst:
					# you have some options on how to actually execute the program here.
					futs.append(executor.submit(check_correctness, file_name, grammar_name, timeout=12000, sub_process=ix))
			ix = ix + 1
	
		for f in tqdm(cfuts.as_completed(futs), total=len(futs)):
			result = f.result()
			cid = result['completion_id']
			if result["passed"] != "timeout" and result["passed"] != "char error":
				with open(cid, "r") as file:
					line = file.read()
				result["lines"] = line
			remove_files.append(cid)
			validator_results.append(result)
		

	for file_to_remove in remove_files:
		remove_tmp_file(file_to_remove)

	with open(results_file, "w") as rf:
		for r in validator_results:
			rf.write(json.dumps(r) + '\n')

if __name__ == '__main__':
	""" Evaluate code from generative models versus a valid grammar """
	""" Example usage: python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="Numpy" --parallel=False """
	""" Example usage: python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True """
	""" Example usage: python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="odex" """
	""" Example usage: python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex" """
	
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--codetest", help="File JSON containing the generated code.")
	parser.add_argument("--model", help="Name of the model to evaluate.")
	parser.add_argument("--answer", help="Evaluate either the answer or error version.")
	parser.add_argument("--library", help="Library name to evaluate.")
	parser.add_argument("--parallel", help="Evaluation processing method.")
	parser.add_argument("--split", help="Split lines by end of line. ")
	parser.add_argument("--test", type=str, default="DS", 
        choices=["DS", "odex", "bigcodebench"])

	args = parser.parse_args()
	if eval(args.parallel):
		evaluate_code_grammar(args.codetest, args.model, eval(args.answer), args.library, args.test, eval(args.split))
	else:
		sequential_evaluate(args.codetest, args.model, eval(args.answer), args.library, args.test, eval(args.split))


