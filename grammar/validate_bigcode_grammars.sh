#!/bin/bash

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-turbo-0125-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/ibm-granite-0-answers.jsonl" --model="granite-code-latest-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/gemma2-2b-0-answers.jsonl" --model="gemma2-2b-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False

python validate_grammar.py --codetest="../../Library-Bench/bigcodebench/results/qwen3-8b-0-answers.jsonl" --model="qwen3-8b-0" --answer=True --library="" --parallel=True --test="bigcodebench" --split=False