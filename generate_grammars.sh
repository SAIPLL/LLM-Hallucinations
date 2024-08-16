#!/bin/bash

python grammar/module_to_schema.py --module='pandas' --file='Data/graph4code/output/modules_out/pandas/pandas.json' --kwargs=False

python grammar/module_to_schema.py --module='sklearn' --file='Data/graph4code/output/modules_out/sklearn/sklearn.json' --kwargs=False

python grammar/module_to_schema.py --module='scipy' --file='Data/graph4code/output/modules_out/scipy/scipy.json' --kwargs=False

python grammar/module_to_schema.py --module='torch' --file='Data/graph4code/output/modules_out/torch/torch.json' --kwargs=False

python grammar/module_to_schema.py --module='tensorflow' --file='Data/graph4code/output/modules_out/tensorflow/tensorflow.json' --kwargs=False

python grammar/write_grammar.py --lst-function='pandas.txt' --baseline-grammar='grammar/any.gbnf' --alias="['pd']" --name="['pandas']"

python grammar/write_grammar.py --lst-function='sklearn.txt' --baseline-grammar='grammar/any.gbnf' --alias="['sklearn']" --name="['sklearn']"

python grammar/write_grammar.py --lst-function='scipy.txt' --baseline-grammar='grammar/any.gbnf' --alias="['scipy']" --name="['scipy']"

python grammar/write_grammar.py --lst-function='torch.txt' --baseline-grammar='grammar/any.gbnf' --alias="['torch']" --name="['torch']"

python grammar/write_grammar.py --lst-function='tensorflow.txt' --baseline-grammar='grammar/any.gbnf' --alias="['tf']" --name="['tensorflow']"