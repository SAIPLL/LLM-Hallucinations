#!/bin/bash

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="odex" --split=False

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/gpt-3.5-turbo-0125/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-turbo-0125-0" --answer=True --library="" --parallel=True --test="odex" --split=False

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="odex" --split=False

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/granite-code-latest/granite-code-latest-0-answers.jsonl" --model="granite-code-latest-0" --answer=True --library="" --parallel=True --test="odex" --split=False

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/gemma2-2b/gemma2-2b-0-answers.jsonl" --model="gemma2-2b-0" --answer=True --library="" --parallel=True --test="odex" --split=False

python validate_grammar.py --codetest="../../Library-Bench/odex/data/nl2code/qwen3-8b/qwen3-8b-0-answers.jsonl" --model="qwen3-8b-0" --answer=True --library="" --parallel=True --test="odex" --split=False