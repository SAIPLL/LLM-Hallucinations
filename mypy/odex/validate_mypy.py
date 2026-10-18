"""
	This script evaluates faithful code using the gbnf-validator
"""

import argparse
import json
import os
import re
import subprocess
import concurrent.futures as cfuts
from tqdm import tqdm
import time


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

def heavy_postprocess(code):
    # ollama model outputs all types of formats
    if type(code) is list:
        code = code[0]
    # Tokenize by end of line
    lines = code.split('\n')
    # Add except
    new_code = []
    for l in lines:
        if l.startswith("import"):
            new_code.append(l)
        elif l.startswith("from"):
            new_code.append(l)
        elif '"""' in l:
            new_code.append("")
        elif l.startswith("#"):
            new_code.append(l)
        elif l.startswith("def"):
            new_code.append(l)
        elif l.startswith("for"):
            new_code.append(l)
        elif l.startswith("if"):
            new_code.append(l)
        elif l.startswith("```python"):
            new_code.append("")
        elif "END SOLUTION" in l:
            new_code.append("")
        elif "<code>" in l:
            new_code.append("")
        elif "</code>" in l:
            new_code.append("")
        elif "..." in l:
            new_code.append("")
        elif "=" in l:
            new_code.append(l)
        elif "`" in l:
            new_code.append("")
        elif "(" in l:
            new_code.append(l)
        elif l.startswith(" "):
            new_code.append(l)
        else:
            new_code.append("")
    result = "\n".join(new_code)
    if len(result) < 1:
        result = postprocess(code)
    return result

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

def get_imports(test_str):
	import_lines = []
	code = data_line["test_start"].split('\n')
	for c in code:
		if "import" in c:
			import_lines.append(c)
	return "\n".join(import_lines)

def write_str_file(file_model, code_info, question, library_name, is_answer, split_lines=False, test_name="DS"):
	"""
		Write the file into a string
	"""
	# Write code answer only
	if is_answer:
		file_to_write = f"{file_model}_{code_info['id']}.py"
		code = code_info["code"]
	else:
		file_to_write = f"{file_model}_{code_info['completion_id']}.py"
		code = code_info["generate_code"]
	if test_name != 'bigcodebench':
		extracted_code = postprocess(code)
		extracted_code = clean_code(extracted_code)
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
		context_code = ""
		if test_name == "DS":
			extracted_code += "\n"
			# Regex to find the content within the first <code>...</code>
			match = re.search(r"<code>(.*?)</code>", question["prompt"], re.DOTALL)
			# Extract the content if a match is found
			if match:
			    context_code = match.group(1).strip()
			else:
			    fallback_match = re.search(r"<code>(.*?)(END SOLUTION|BEGIN SOLUTION)", question["prompt"], re.DOTALL)
			    if fallback_match:
			        context_code = fallback_match.group(1).strip()
			    else:
			        context_code = question["prompt"]
		elif test_name == "odex":
			if "test_start" in code_info:
				context_code = get_imports(code_info["test_start"])
			if "def f_" not in extracted_code:
				if "prompt" in code_info:
					context_code += code_info["prompt"]
		context_code += "\n"
		code_to_write = context_code + extracted_code
		# without cleaning
		code_to_write = extracted_code
		with open(file_to_write, "w") as f:
			f.write(code_to_write)
		f.close()
		return [file_to_write]

def get_parse_result(output_str):
	"""
		String passes or not the generation
	"""
	# Regular expression to match the number after "errorCount"
	match = re.search(r'"severity": "error"', output_str)

	result = "pass"
	# Check if a match was found and extract the number
	if match:
	    result = "Error"
	else:
		match = re.search(r'"error:', output_str)
		if match:
			result = "Error"

	return result, output_str

def check_correctness(file_name, timeout=12000, sub_response=0):
	"""
		Executes the grammar validation of a program
		Timeout = 900
	"""

	# Path to the C++ binary
	binary_path = 'mypy --output=json'
	instruction = f'{binary_path} {file_name}'
	start_time = 0
	end_time = 0

	try:
		start_time = time.time()
		result_sub = subprocess.run(instruction, stdout=subprocess.PIPE, stderr=None, text=True, shell=True, timeout=timeout)
		end_time = time.time()
		output, lines = get_parse_result(result_sub.stdout)
	except subprocess.TimeoutExpired:
		# result_sub.kill()
		output = "timeout"
		lines = ""
	except Exception as e:
		output = f"char error: {str(e)}"  # Capture the actual error message
		lines = ""
	
	total_time = end_time - start_time
	
	return dict(
		passed=output,
		result=lines,
		completion_id=file_name,
		time=total_time,
		cid=sub_response
	)

def sequential_evaluate(code_file, model_name, is_answer, library="", test_name="DS", split_lines=False):
	"""
		Test generation on grammar in a sequential manner
	"""

	results_file = f"{model_name}_mypy_validation.jsonl"

	results = [json.loads(l) for l in open(code_file, "r")]
	validator_results = []
	ix = 0
	if test_name == 'bigcodebench':
		lib_col = 'libs'
	else:
		lib_col = 'library'
	
	for code_test in results:
		if is_answer:
			library_name = code_test['metadata'][lib_col]
		else:
			library_name = code_test[lib_col]
		
		if library_name == library or library == "":
			file_names_lst = write_str_file(model_name, code_test, library_name, is_answer, split_lines=split_lines, test_name=test_name)
			for file_name in file_names_lst:
				response = check_correctness(file_name, timeout=12000, sub_response=ix)
				cid = response['completion_id']
				remove_tmp_file(cid)
				validator_results.append(response)
		ix = ix+1

	with open(results_file, "w") as rf:
		for r in validator_results:
			rf.write(json.dumps(r) + '\n')

def find_example(odex_example, odex_id):
	for ex in odex_example:
		print(ex['id'], odex_id)
		if str(ex['id']) == str(odex_id):
			return ex['metadata']['library']

def evaluate_code_grammar(code_file, model_name, is_answer, library, test_name, split_lines=False):
	"""
		Compare output from generation to grammar
	"""
	
	results_file = f"{model_name}_mypy_validation.jsonl"

	results = [json.loads(l) for l in open(code_file, "r")]

	#questions = [json.loads(l) for l in open("../../Library-Bench/DS-1000/data/ds1000.jsonl", "r")]

	odex_example = [json.loads(l) for l in open("../../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl", "r")]

	remove_files = []
	
	validator_results = []
	with cfuts.ProcessPoolExecutor(
		max_workers=16
	) as executor:
		futs = []
		ix=0
		for code_test in results:
			if test_name == 'bigcodebench':
				lib_col = 'libs'
			else:
				lib_col = 'library'

			if test_name == 'DS':
				question = questions[ix]
			else:
				question = None
			
			if test_name == 'odex' and model_name in ['gemma2-2b', 'qwen3-8b']:
					library_name = find_example(odex_example, code_test['id'])
			else:
				if test_name == 'bigcodebench' :
					library_name = json.loads(code_test['metadata'])[lib_col]
				else:
					library_name =  code_test['metadata'][lib_col]
			
			if library_name == library or library == "":
				file_names_lst = write_str_file(model_name, code_test, question, library_name, is_answer, split_lines=split_lines, test_name=test_name)
				
				for file_name in file_names_lst:
					# you have some options on how to actually execute the program here.
					futs.append(executor.submit(check_correctness, file_name, timeout=12000,sub_response=ix))
			ix = ix+1
	
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
	""" Example usage: python validate_mypy.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="Numpy" --parallel=False """
	""" Example usage: python validate_mypy.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --split=False """
	""" Example usage: python validate_mypy.py --codetest="../../Library-Bench/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="odex" """
	""" Example usage: python validate_mypy.py --codetest="../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex" """
	
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