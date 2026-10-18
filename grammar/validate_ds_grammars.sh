#!/bin/bash

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-0125-0" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/granite-code:latest-no-grammar-0-answers.jsonl" --model="granite-code:latest-no-grammar-0" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-3.5-turbo-0613-0-answers.jsonl" --model="gpt-3.5-0613-0" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gpt-4-turbo-2024-04-09-0-answers.jsonl" --model="gpt-4-turbo-2024-04-09-0" --answer=True --library="" --parallel=True --split=True

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/gemma2-2b-0-answers.jsonl" --model="gemma2-2b-0" --answer=True --library="" --parallel=True --split=False

python validate_grammar.py --codetest="../../Library-Bench/DS-1000/data/qwen3-8b-0-answers.jsonl" --model="qwen3-8b-0" --answer=True --library="" --parallel=True --split=False

