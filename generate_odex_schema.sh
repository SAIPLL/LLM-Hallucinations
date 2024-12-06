#!/bin/bash

python grammar/module_to_schema.py --module='glob' --file='Data/graph4code/output/odex/glob/glob.json' --kwargs=True
python grammar/module_to_schema.py --module='filecmp' --file='Data/graph4code/output/odex/filecmp/filecmp.json' --kwargs=True
python grammar/module_to_schema.py --module='functools' --file='Data/graph4code/output/odex/functools/functools.json' --kwargs=True
python grammar/module_to_schema.py --module='io' --file='Data/graph4code/output/odex/io/io.json' --kwargs=True
python grammar/module_to_schema.py --module='itertools' --file='Data/graph4code/output/odex/itertools/itertools.json' --kwargs=True
python grammar/module_to_schema.py --module='multidict' --file='Data/graph4code/output/odex/multidict/multidict.json' --kwargs=True
python grammar/module_to_schema.py --module='pickle' --file='Data/graph4code/output/odex/pickle/pickle.json' --kwargs=True
python grammar/module_to_schema.py --module='sys' --file='Data/graph4code/output/odex/sys/sys.json' --kwargs=True
python grammar/module_to_schema.py --module='warnings' --file='Data/graph4code/output/odex/warnings/warnings.json' --kwargs=True
python grammar/module_to_schema.py --module='urllib.parse' --file='Data/graph4code/output/odex/urllib.parse/urllib.parse.json' --kwargs=True
python grammar/module_to_schema.py --module='urllib.request' --file='Data/graph4code/output/odex/urllib.request/urllib.request.json' --kwargs=True
python grammar/module_to_schema.py --module='time' --file='Data/graph4code/output/odex/time/time.json' --kwargs=True
python grammar/module_to_schema.py --module='datetime' --file='Data/graph4code/output/odex/datetime/datetime.json' --kwargs=True