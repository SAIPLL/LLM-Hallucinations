# Detector of hallucinations tests

## Test cases classification

### Library 
- Simple call
- Two libraries
- Library as a parameter
- Library inside a data type
- Subscriptable library

### Data types (the value rule)
- Tuple
- Array
- Function call non-library
- Other class non-library

### Operation expression
- Conditionals
- Arithmetic

## Test cases for grammar validation
test-1.txt: function call non-library, tuple, other class non-library
test-2.txt: function call library, library as a parameter, subscriptable library
test-3.txt: other class non-library as a parameter on library call
test-4.txt: library simple call with unordered parameters
test-5.txt: enum only (should not work)
test-6.txt: arithmetic expressions inside a library call
test-7.txt: function call non-library, tuple, in library
test-8.txt: arithmetic expressions inside a library call, other class non-library larger class name
test-9.txt: ufunction test in Numpy
test-10.txt: negation (~) operator in Numpy
test-11.txt: library function separated by end of line
test-12.txt: library "tf" as, both, name and alias
test-13.txt: library function everything optional
test-14.txt: library function as function name
test-15.txt: name non-library, subscriptable