# Hallucinations

The first part of the project brings different benchmarks from which we obtained hallucinated programs from code generation.
Running those benchmarks (within its environment) and finding the buggy programs along its error messages has represented several changes. These modifications and fixes, from its original, are being tracked in this repository.

## Data

### [CoderEval](https://github.com/CoderEval/CoderEval)

To get the sample generated code and run it within the environment, there is this [docker image](https://drive.google.com/drive/folders/11Ox27cV4spP-_ly-GK6qAh6EG7TxwYh1?usp=sharing).

I am providing a modification to ```Data/CoderEval/PythonExec.py``` to save the error message.

```sh
docker run image

# Once in the image
cd /home/travis/builds/ 

vim PythonExec.py

python PythonExec.py ./GenerateResultPython/CodeGen/Raw_Input.jsonl 10
```

To copy a file from the image to local:

```sh
docker cp <image_id>:<source_path> <local_destination_path>
```

### [DS-1000](https://github.com/xlang-ai/DS-1000)

I have edited ```Data/DS-1000/execution.py``` and ```Data/DS-1000/test_ds1000.py``` to provide more information and format about the error message.
I have updated ```Data/DS-1000/run_openai.py``` to receive arguments to call the OpenAI API.
I have included a call to the Anthropic API through this script ```Data/DS-1000/run_claude.py```.
I have included a call to the Ollama API (running locally) through this script ```Data/DS-1000/run_ollama.py```.

```
cd DS-1000
python run_ollama.py
```

## KGs

### [GraphGen4code](https://github.com/wala/graph4code/tree/master)

Here is the information to load [Graph4Code](https://github.com/wala/graph4code?tab=readme-ov-file#collecting-documentation-docstrings-for-your-scripts).

The original code in graph4code, only works for libraries in pip (ex. matplotlib, numpy...). These code has been moved to ```Data/graph4code/scripts/inspect-modules_for_docstrings_standalone.sh```. You can inspect a module using:

```
sh inspect_modules_for_docstrings_standalone.sh ../output/top_modules.json ../output/modules_out/ ~/anaconda3/ False
```

I updated  ```Data/graph4code/scripts/inspect-modules_for_docstrings.sh``` to work with standard libraries, such as: math or string.

```
sh inspect_modules_for_docstrings.sh ../output/top_modules.json ../output/modules_out/ ~/anaconda3/ False
```

The last argument is a boolean and indicates whether the library should be downloaded (True, else False). 
Also, the python scripts have been edited ```Data/graph4code/src/inspect-docstrings_per_module.py``` to store the json file locally without Elasticsearch.

### [Graph4Code to JSON Schema to GBNF]

The resulting JSON from GraphGen4code needs to be transform to JSON Schema and then to a grammar of the form GBNF. This is an example for generating the `matplotlib.pyplot` grammar: 

```
python grammar/module_to_schema.py --module='matplotlib.pyplot' --file='Data/graph4code/output/modules_out/matplotlib.pyplot/matplotlib.pyplot.json' --kwargs=False
```

```
python grammar/write_grammar.py --lst-function='matplotlib.pyplot.txt' --baseline-grammar='grammar/any.gbnf' --alias="['plt']" --name="['matplotlib.pyplot']"
```

## Model 

#### [Ollama](https://github.com/ollama/ollama?tab=readme-ov-file#building)

I am using the open-source Ollama framework to run LLMs locally. I have modify Ollama's client API to receive a grammar. This way we can pass the grammar to llama.cpp and constrained the decoder with the specified grammar. This approach let you guide any model being hosted in Ollama.

``` 
./ollama serve 
```

[More info to build a modified ollama.](https://github.com/ollama/ollama/blob/main/docs/development.md)