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
I have included a call to the Anthropic API through this script ```Data/DS-1000/run_claude.py```.
I have updated ```Data/DS-1000/run_openai.py``` to receive arguments to call the OpenAI API.

## KGs

### [GraphGen4code](https://github.com/wala/graph4code/tree/master)

Here is the information to load [Graph4Code](https://github.com/wala/graph4code/blob/master/docs/load_graph.md).
I had to edit ```graph4code/scripts/build_graph.sh```. This modification updated an url, which now points out to the archive.

## Model 

#### [CodeGen](https://github.com/salesforce/CodeGen)

I am using the open-source model for code generation CodeGen, this model can be download from huggingface [here](https://huggingface.co/Salesforce/codegen25-7b-mono_P).