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

def write_str_file(file_model, code_info, library_name, is_answer, split_lines=False):
	"""
		Write the file into a string
	"""
	# Write code answer only
	if is_answer:
		file_to_write = f"{file_model}_{code_info['id']}"
		code = code_info["code"]
	else:
		file_to_write = f"{file_model}_{code_info['completion_id']}"
		code = code_info["generate_code"]
	extracted_code = postprocess(code)
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
	print(output_str)
	if error_index > 0:
		# Find error substring
		error_line = output_str[error_index:]
		# Find end of line index
		eof_idx = error_line.find("\n")
		result = error_line[:eof_idx]
		if "Unexpected end of input" in result:
			result = "unexpected"
	else:
		result = "pass"

	return result, output_str

def check_correctness(file_name, grammar, timeout=12000):
	"""
		Executes the grammar validation of a program
		Timeout = 900
	"""

	# Path to the C++ binary
	binary_path = './llama-gbnf-validator'
	instruction = f'{binary_path} {grammar} {file_name}'

	try:
		result_sub = subprocess.run([instruction], stdout=subprocess.PIPE, stderr=None, text=True, shell=True, timeout=timeout)
		output, lines = get_parse_result(result_sub.stdout)
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
		completion_id=file_name
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
		if is_answer:
			library_name = code_test['metadata']['library']
		else:
			library_name = code_test['library']
		if library_name == library or library == "":
			if test_name == "odex":
				grammar_name = f"files/odex/{code_test['lang']}_{code_test['id']}-atomtest-grammar.gbnf"
			else:
				grammar_name = f"files/{library_name.lower()}-atomtest-grammar.gbnf"
			file_names_lst = write_str_file(model_name, code_test, library_name, is_answer, split_lines=split_lines)
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


def evaluate_code_grammar(code_file, model_name, is_answer, library, test_name, split_lines=False):
	"""
		Compare output from generation to grammar
	"""
	
	results_file = f"{model_name}_grammar_validation.jsonl"

	results = [json.loads(l) for l in open(code_file, "r")]

	remove_files = []
	
	validator_results = []
	with cfuts.ProcessPoolExecutor(
		max_workers=16
	) as executor:
		futs = []
		for code_test in results:
			if is_answer:
				library_name = code_test['metadata']['library']
			else:
				library_name = code_test['library']
			
			if library_name == library or library == "":
				if test_name == "odex":
					grammar_name = f"files/odex/{code_test['lang']}_{code_test['id']}-atomtest-grammar.gbnf"
				else:
					grammar_name = f"files/{library_name.lower()}-atomtest-grammar.gbnf"
				file_names_lst = write_str_file(model_name, code_test, library_name, is_answer, split_lines=split_lines)
				
				for file_name in file_names_lst:
					# you have some options on how to actually execute the program here.
					futs.append(executor.submit(check_correctness, file_name, grammar_name, timeout=12000))
	
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
	""" Example usage: python validate_grammar.py --codetest="../Data/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="Numpy" --parallel=False """
	""" Example usage: python validate_grammar.py --codetest="../Data/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True """
	""" Example usage: python validate_grammar.py --codetest="../Data/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="odex" """
	""" Example usage: python validate_grammar.py --codetest="../Data/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex" """
	
	parser = argparse.ArgumentParser(description="Write grammar to constraint the inference of non-standalone code.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--codetest", help="File JSON containing the generated code.")
	parser.add_argument("--model", help="Name of the model to evaluate.")
	parser.add_argument("--answer", help="Evaluate either the answer or error version.")
	parser.add_argument("--library", help="Library name to evaluate.")
	parser.add_argument("--parallel", help="Evaluation processing method.")
	parser.add_argument("--split", help="Split lines by end of line. ")
	parser.add_argument("--test", type=str, default="DS", 
        choices=["DS", "odex"])

	args = parser.parse_args()
	if eval(args.parallel):
		evaluate_code_grammar(args.codetest, args.model, eval(args.answer), args.library, args.test, eval(args.split))
	else:
		sequential_evaluate(args.codetest, args.model, eval(args.answer), args.library, args.test, eval(args.split))



