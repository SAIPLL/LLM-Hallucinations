#!/bin/bash

python validate_grammar.py --codetest="../Data/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex"

python validate_grammar.py --codetest="../Data/odex/data/nl2code/gpt-3.5-turbo-0125/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-turbo-0125-0" --answer=True --library="" --parallel=True --test="odex"

python validate_grammar.py --codetest="../Data/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="odex"

python validate_grammar.py --codetest="../Data/odex/data/nl2code/granite-code-latest/granite-code-latest-0-answers.jsonl" --model="granite-code-latest-0" --answer=True --library="" --parallel=True --test="odex"