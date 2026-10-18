# Hallucinations

The first part of the project brings different benchmarks from which we obtained hallucinated programs from code generation.
Running those benchmarks (within its environment) and finding the buggy programs along its error messages has represented several changes. These modifications and fixes, from its original, are being tracked in the repo [Library-Bench](https://github.com/SAIPLL/Library-Bench.git))

## KGs

### [GraphGen4code](https://github.com/wala/graph4code/tree/master)

Here is the information to load [Graph4Code](https://github.com/wala/graph4code?tab=readme-ov-file#collecting-documentation-docstrings-for-your-scripts).

The original code in graph4code, only works for libraries in pip (ex. matplotlib, numpy...). These code has been moved to ```Data/graph4code/scripts/inspect_modules_for_docstrings_standalone.sh```. You can inspect a module and standard libraries (such as: math or string) using:

```
cd scripts
sh inspect_modules_for_docstrings_standalone.sh ../output/top_modules.json ../output/modules_out/ ~/anaconda3/ False
```

The last argument is a boolean and indicates whether the library should be downloaded (True, else False). 
Also, the python scripts have been edited ```Data/graph4code/src/inspect-docstrings_per_module.py``` to store the json file locally without Elasticsearch.

I am providing `top_modules_ds.json` with all the list of libraries required for DS-1000 and Odex. While additional BigCodeBench libraries are in `top_modules.json`.

### Graph4Code to JSON Schema to GBNF

The resulting JSON from GraphGen4code needs to be transform to JSON Schema and then to a grammar of the form GBNF. This is an example for generating the `matplotlib.pyplot` grammar: 

```
python grammar/module_to_schema.py --module='matplotlib.pyplot' --file='Data/graph4code/output/modules_out/matplotlib.pyplot/matplotlib.pyplot.json' --kwargs=True --starts=True
```
Note: this heavily depends on `grammar/json_function_to_grammar.py` this is the core code to create the grammar.

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

To set everything for BigCodeBench run:
```
python grammar/generate_bigcodebench_grammar.py 
```

Lists produced by GraphGen4code are contained in `libraries.zip` while `gbnfs.zip` contains the generated grammars `grammar/files/` used by the validator, and filtered with `grammar/odex_grammar_mapping.jsonl` and `grammar/bigcodebench_mapping.json`.

## Model 

#### [Ollama](https://github.com/ollama/ollama?tab=readme-ov-file#building)

I am using the open-source Ollama framework to run LLMs locally. I have [modify Ollama's client API](https://github.com/ollama/ollama/pull/15408) to receive a grammar. This way we can pass the grammar to llama.cpp and constrained the decoder with the specified grammar. This approach let you guide any model being hosted in Ollama.

``` 
./ollama serve 
```

To save the ollama's server log with the "Resampling info", I am starting ollama with the following command.
```
./ollama serve > output_file_name 2>&1 
./ollama serve > ollama_grammar.txt 2>&1 
```

[More info on how to build a modified Ollama.](https://github.com/ollama/ollama/blob/main/docs/development.md)

#### Grammar Validator (Detector)

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

#### Static tools Validator

##### Type-stubs support
You can use the list in `top_modules_<benchmark>.json` in the graph4code folder to get the type-stubs for each of the benchmark.
For example, run `pyright/bigcodebench/create_stub_bigcodebench_third_party.sh` to get the type-stubs for BigCodeBench.

##### Mypy validation
```
cd mypy
./validate_mypy.sh
```

##### Pyright validation
```
cd pyright
./validate_pyright.sh
```



