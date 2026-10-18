#!/bin/bash
# Run the grammar regression tests: each entry is "<library> <grammar variant> <test file>".
# Usage (from grammar/): ./test_grammar.sh
# Needs the llama-gbnf-validator binary in this folder and the grammars in files/ (unzip ../gbnfs.zip).

VALIDATOR=./llama-gbnf-validator

TESTS=(
  "matplotlib atomimport test_validation.txt"
  "numpy atomimport test-grammar/test-28.txt"
  "pandas atomimport test-grammar/test-29.txt"
  "pandas atomimport test-grammar/test-30.txt"
  "pandas atomimport test-grammar/test-26.txt"
  "pandas atomimport test-grammar/test-27.txt"
  "pandas atomimport test-grammar/test-1.txt"
  "numpy atomimport test-grammar/test-1.txt"
  "pytorch atomimport test-grammar/test-1.txt"
  "tensorflow atomimport test-grammar/test-1.txt"
  "sklearn atomimport test-grammar/test-1.txt"
  "scipy atomimport test-grammar/test-1.txt"
  "pandas atomtest test-grammar/test-5b.txt"
  "pandas atomexpr test-grammar/test-5b.txt"
  "pandas atomtest test-grammar/test-1.txt"
  "pandas atomtest test-grammar/test-2.txt"
  "pandas atomtest test-grammar/test-3.txt"
  "pandas atomtest test-grammar/test-4.txt"
  "pandas atomtest test-grammar/test-5.txt"
  "pandas atomexpr test-grammar/test-5c.txt"
  "pandas atomtest test-grammar/test-6.txt"
  "pandas atomtest test-grammar/test-7.txt"
  "pandas atomtest test-grammar/test-8.txt"
  "pandas atomtest test-grammar/test-9.txt"
  "pandas atomtest test-grammar/test-10.txt"
  "pandas atomtest test-grammar/test-11.txt"
  "tensorflow atomexpr test-grammar/test-12.txt"
  "pandas atomtest test-grammar/test-13.txt"
  "pandas atomtest test-grammar/test-14.txt"
  "pandas atomtest test-grammar/test-15.txt"
  "pandas atomtest test-grammar/test-16.txt"
  "pandas atomtest test-grammar/test-17.txt"
  "tensorflow atomexpr test-grammar/test-18.txt"
  "pytorch atomexpr test-grammar/test-19.txt"
  "numpy atomtest test-grammar/test-24.txt"
)

for t in "${TESTS[@]}"; do
  read -r lib kind file <<< "$t"
  echo "== $lib ($kind) <- $file"
  "$VALIDATOR" "files/$lib-$kind-grammar.gbnf" "$file"
done
