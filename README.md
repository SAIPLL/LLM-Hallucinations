# Hallucinations

The first part of the project brings different benchmarks from which we obtained hallucinated programs from code generation.
Running those benchmarks (within its environment) and finding the buggy programs along its error messages has represented several changes. These modifications and fixes, from its original, are being tracked in this repository.

## Data

### [DS-1000](https://github.com/xlang-ai/DS-1000)

I have edited ```Data/DS-1000/execution.py``` and ```Data/DS-1000/test_ds1000.py``` to provide more information and format about the error message.
I have updated ```Data/DS-1000/run_openai.py``` to receive arguments to call the OpenAI API.
I have included a call to the Anthropic API through this script ```Data/DS-1000/run_claude.py```.
I have included a call to the Ollama API (running locally) through this script ```Data/DS-1000/run_ollama.py```.

```
cd Data/DS-1000
python run_ollama.py
```

To run ollama with the grammar for a specific library

```
python run_ollama.py --grammar "True" --library "Numpy"
```
For any library:
```
python run_ollama.py --grammar "True" --library ""
```

### [Odex](https://github.com/zorazrw/odex)

I have edited Odex ```Data/odex/nl2code_codex.py``` to work with OpenAI's chat API, as well as Anthropic Messages. As in pass@1 the default `temperature=0.2` and `n=1`. I have skipped the prompts in the dataset that doens't belong to the `"open"` domain.

```
cd Data/odex
python nl2code_codex.py --language es --model_name "claude-3-opus-20240229"
python nl2code_codex.py --language es --model_name "gpt-4-0613"
python nl2code_codex.py --language es --model_name "gpt-3.5-turbo-0125"
python nl2code_codex.py --language es --model_name "granite-code:latest"
python nl2code_codex.py --language es --model_name "granite-code:latest" --grammar True
```

Run odex re-evaluation.

```
pip install -r ./library/requirements.txt 
python ./library/imports.py

python eval_passk.py --language es --prediction_path data/nl2code/claude-3-opus-20240229/es_pred_0-0.json --library_usage "open"
```

To format the results in odex to work with the validator script.
```
python format_odex_validation.py
```

## KGs

### [GraphGen4code](https://github.com/wala/graph4code/tree/master)

Here is the information to load [Graph4Code](https://github.com/wala/graph4code?tab=readme-ov-file#collecting-documentation-docstrings-for-your-scripts).

The original code in graph4code, only works for libraries in pip (ex. matplotlib, numpy...). These code has been moved to ```Data/graph4code/scripts/inspect-modules_for_docstrings_standalone.sh```. You can inspect a module and standard libraries (such as: math or string) using:

```
sh inspect_modules_for_docstrings_standalone.sh ../output/top_modules.json ../output/modules_out/ ~/anaconda3/ False
```

The last argument is a boolean and indicates whether the library should be downloaded (True, else False). 
Also, the python scripts have been edited ```Data/graph4code/src/inspect-docstrings_per_module.py``` to store the json file locally without Elasticsearch.

I am providing `top_modules.json` with all the list of libraries required for DS-1000 and Odex.

### Graph4Code to JSON Schema to GBNF

The resulting JSON from GraphGen4code needs to be transform to JSON Schema and then to a grammar of the form GBNF. This is an example for generating the `matplotlib.pyplot` grammar: 

```
python grammar/module_to_schema.py --module='matplotlib.pyplot' --file='Data/graph4code/output/modules_out/matplotlib.pyplot/matplotlib.pyplot.json' --kwargs=True
```

```
python grammar/write_grammar.py --lst-function='matplotlib.pyplot.txt' --baseline-grammar='grammar/any.gbnf' --alias="['plt']" --name="['matplotlib.pyplot']"
```

You can also create a grammar of multiple libraries:
```
python grammar/write_grammar.py --lst-function='dsall.txt' --baseline-grammar='grammar/final.gbnf' --alias="['np','pd']" --name="['numpy','pandas']" --lst-namespace='filter.txt'
```

To filter the libraries' private namespaces, you can list the submodules you want to include in a file:
````
python grammar/write_grammar.py --lst-function='dsall.txt' --baseline-grammar='grammar/any.gbnf' --alias="['np','pd','sklearn','scipy','matplotlib','plt','torch','tf']" --name="['numpy','pandas','sklearn','scipy','matplotlib','matplotlib.pyplot','pytorch','tensorflow']" --lst-namespace='filter.txt'
````

To set everything for DS-1000 run:

```
cd LLM-Hallucinations
./generate_ds_grammar.sh
```

To set everything for Odex run:
```
python grammar/generate_odex_grammar.py
```

## Model 

#### [Ollama](https://github.com/ollama/ollama?tab=readme-ov-file#building)

I am using the open-source Ollama framework to run LLMs locally. I have modify Ollama's client API to receive a grammar. This way we can pass the grammar to llama.cpp and constrained the decoder with the specified grammar. This approach let you guide any model being hosted in Ollama.

``` 
./ollama serve 
```

To save the ollama's server log with the "Resampling info", I am starting ollama with the following command.
```
./ollama serve > output_file_name 2>&1 
./ollama serve > ollama_grammar.txt 2>&1 
```

[More info on how to build a modified Ollama.](https://github.com/ollama/ollama/blob/main/docs/development.md)

#### Validator (Detector)

##### [llama.cpp](https://github.com/clarismiranda/llama.cpp/tree/grammar-memo)
I have made some changes in llama.cpp grammar validator script `examples/llama-gbnf-validator` and its dependencies on `llama-grammar`.

To get the validator running, first you need to [build llama](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md), and copy the binary into the grammar folder of this repo.

```
cd grammar
python validate_grammar.py --codetest="../Data/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex"
python validate_grammar.py --codetest="../Data/DS-1000/data/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True
```

To validate everything for DS-1000 run:

```
cd grammar
./validate_ds_grammars.sh
```

To validate everything for Odex run:
```
cd grammar
./validate_odex_grammars.sh
```
