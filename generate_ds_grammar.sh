#!/bin/bash

#python grammar/module_to_schema.py --module='scipy' --file='Data/graph4code/output/modules_out/scipy/scipy.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='numpy' --file='Data/graph4code/output/modules_out/numpy/numpy.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='matplotlib' --file='Data/graph4code/output/modules_out/matplotlib/matplotlib.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='matplotlib.pyplot' --file='Data/graph4code/output/modules_out/matplotlib.pyplot/matplotlib.pyplot.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='pandas' --file='Data/graph4code/output/modules_out/pandas/pandas.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='sklearn' --file='Data/graph4code/output/modules_out/sklearn/sklearn.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='torch' --file='Data/graph4code/output/modules_out/torch/torch.json' --kwargs=True --starts=True

#python grammar/module_to_schema.py --module='tensorflow' --file='Data/graph4code/output/modules_out/tensorflow/tensorflow.json' --kwargs=True --starts=True

python grammar/write_grammar.py --lst-function='files/pandas.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','pd']" --name="['numpy','pandas']" --lst-namespace='files/filter1.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/sklearn.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','pd','sklearn']" --name="['numpy','pandas','sklearn']" --lst-namespace='files/filter2.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/matplotlib.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','pd','plt','matplotlib']" --name="['numpy','pandas','matplotlib.pyplot','matplotlib']" --lst-namespace='files/filter3.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/scipy.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','scipy']" --name="['numpy','scipy']"  --lst-namespace='files/filter4.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/pytorch.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','torch']" --name="['numpy','pytorch']"  --lst-namespace='files/filter5.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/tensorflow.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np','tf']" --name="['numpy','tensorflow']"  --lst-namespace='files/filter6.txt' --name-alias=True

python grammar/write_grammar.py --lst-function='files/numpy.txt' --baseline-grammar='grammar/atomimport.gbnf' --alias="['np']" --name="['numpy']"  --lst-namespace='files/filter7.txt' --name-alias=True