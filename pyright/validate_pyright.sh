#!/bin/bash

cd bigcodebench

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/ibm-granite-0-answers.jsonl" --model="granite-code:latest-no-grammar-0" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-0125-0" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/gemma2-2b-0-answers.jsonl" --model="gemma2-2b-0" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"

python validate_pyright.py --codetest="../../../Library-Bench/bigcodebench/results/qwen3-8b-0-answers.jsonl" --model="qwen3-8b-0" --answer=True --library="" --parallel=True --split=False --test="bigcodebench"


cd ../DS

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --split=False

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613" --answer=True --library="" --parallel=True --split=False

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/granite-code:latest-no-grammar-0-answers.jsonl" --model="granite-code:latest-no-grammar-0" --answer=True --library="" --parallel=True --split=False

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-0125-0" --answer=True --library="" --parallel=True --split=False

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/gemma2-2b-0-answers.jsonl" --model="gemma2-2b-0" --answer=True --library="" --parallel=True --split=False

python validate_pyright.py --codetest="../../../Library-Bench/DS-1000/data/qwen3-8b-0-answers.jsonl" --model="qwen3-8b-0" --answer=True --library="" --parallel=True --split=False

cd ../odex

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/claude-3-opus-20240229/claude-3-opus-20240229-0-answers.jsonl" --model="claude-3-opus-20240229-0" --answer=True --library="" --parallel=True --split=False --test="odex"

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/gpt-4-0613/gpt-4-0613-0-answers.jsonl" --model="gpt-4-0613" --answer=True --library="" --parallel=True --split=False --test="odex"

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/granite-code-latest/granite-code-latest-0-answers.jsonl" --model="granite-code-latest-0" --answer=True --library="" --parallel=True --split=False --test="odex"

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/gpt-3.5-turbo-0125/gpt-3.5-turbo-0125-0-answers.jsonl" --model="gpt-3.5-0125" --answer=True --library="" --parallel=True --split=False --test="odex"

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/gemma2-2b/gemma2-2b-0-answers.jsonl" --model="gemma2-2b" --answer=True --library="" --parallel=True --split=False --test="odex"

python validate_pyright.py --codetest="../../../Library-Bench/odex/data/nl2code/qwen3-8b/qwen3-8b-0-answers.jsonl" --model="qwen3-8b" --answer=True --library="" --parallel=True --split=False --test="odex"
