import json
import os
import sys
import gzip
import argparse
import requests
import concurrent.futures as cfuts

from tqdm import tqdm

def call_ollama_api(system="", prompt="something", 
					url="http://localhost:11434/api/generate", 
					grammar="", n_probs=0, top_p=0, temperature=0.2, 
					model="granite-code:latest", keep_alive=-1,
					stop=[], max_tokens=1024, n=1):
	"""
		Call the model with either stop token,
		or n look-ahead tokens
	"""
	
	while True:
		try:
			# Get call
			payload = {
				"model": model,
				"temperature": temperature,
				"prompt": ''.join(prompt),
				"stream": True,
				"options": {},
				"system": system,
				"keep_alive": keep_alive
			}
			
			if n_probs > 0:
				payload["options"]["n_probs"] = n_probs
			if top_p > 0:
				payload["options"]["top_p"] = top_p
			if len(grammar) > 0:
				payload["options"]["grammar"] = grammar
			
			headers = {
				"Content-Type": "application/json"
			}
			
			response = requests.post(url, data=json.dumps(payload), headers=headers)
			break
		except:
			import time; time.sleep(10); pass
	
	# Split the string into individual JSON objects
	json_objects = response.text.strip().split('\n')
	# Parse each JSON object
	parsed_objects = [json.loads(obj) for obj in json_objects]
	r_array = []
	for i in parsed_objects:
		r_array.append(i["response"])
	
	# Instructions
	code = ''.join(r_array)
	#idx_code = code.find('<code>')
	#after_idx = idx_code+len('<code>')
	#code = code[after_idx:]
	return [code]

def run_ollama(model, temperature, idx, with_grammar):
    def get_grammar(library_name="Pandas"):
        """
            Reads a file containing a GBNF grammar
            returns it as a string
        """
        if library_name == "Pytorch":
        	library_name = "torch"
        if library_name == "Matplotlib":
        	library_name = "matplotlib.pyplot"
        file_name = f"../../grammar/{library_name.lower()}-any-grammar.gbnf"

        with open(file_name, 'r') as file:
            content = file.read()
        return content

    def run_func(prompt, id, grammar):
        code = call_ollama_api(
                        # 'Write short code following the problem format and indentation. Do not include formatting tags.',
            'Write a short code following the given format and indentation. Place the executable code between <code> '
            'and </code> tags, without any other non-executable things.',
            prompt,
            grammar=grammar,
            temperature=temperature,
            n=1,
            model=model,
            max_tokens=1024,
            stop=["</code>", "# SOLUTION END"],
        )
        return {'id': id, 'code': code, 'metadata': ds1000[id]['metadata']}

    ds1000_responses = []
    with cfuts.ThreadPoolExecutor(
        max_workers=32
    ) as executor:
        futs = []
        for p in ds1000:
            id = int(p['metadata']['problem_id'])
            prompt = p['prompt']
            if with_grammar:
            	library_needed = p['metadata']['library']
            	library_grammar = get_grammar(library_needed)
            else:
            	library_grammar = ""
            # you have some options on how to actually execute the program here.
            futs.append(executor.submit(run_func, prompt, id, library_grammar))

        for f in tqdm(cfuts.as_completed(futs), total=len(futs)):
            result = f.result()
            ds1000_responses.append(result)
    ds1000_responses.sort(key=lambda x: int(x['id']))
    with open(f'data/{model}-{idx}-answers.jsonl', 'w') as f:
        for r in ds1000_responses:
            f.write(json.dumps(r) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        default="granite-code:latest",
        help="which model to run")
    parser.add_argument(
        "--idx",
        type=str,
        default="0",
        help="index of sample"
    )
    parser.add_argument(
        "--grammar",
        type=str,
        default="False",
        help="to call ollama with grammar"
    )

    ds1000 = [json.loads(l) for l in gzip.open("data/ds1000.jsonl.gz", "rt").readlines()][:1]
    args = parser.parse_args()
    temp = 0.2
    run_ollama(args.model, temp, args.idx, eval(args.grammar))