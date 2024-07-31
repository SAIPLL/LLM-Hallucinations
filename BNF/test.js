import GBNF from 'gbnf';
const state = GBNF(`
root ::= "" importstmt statement* ""
importstmt ::= importname | importfrom
importname ::= "import " dottedasnames

# note below: the ('.' | '...') is necessary because '...' is tokenized as ELLIPSIS
importfrom ::= ( "from " ( ("." | "...")* dottedname | ("." | "...")+ ) " import " ( "*" | "(" importasnames ")" | importasnames ) )
importasname ::= name (" as " name)?
dottedasname ::= dottedname (" as " name)?
importasnames ::= importasname (", " importasname)* (", ")?
dottedasnames ::= dottedasname (", " dottedasname)*
dottedname ::= name ("." name)*

statement ::=
    ( name ws "=" ws expression newline) |
    ( name ws "(" varargslist? ")" newline)

expression ::= term ( ( "+" | "-" ) term)*
term ::= factor ( ( "*" | "@" | "/" | "%" | "//" ) factor)*
factor ::= ( "+" | "-" | "~" ) factor | power
power ::= atomexpr ("**" factor)?
atomexpr ::= atom (trailer)*
atom ::=
    ( "(" (testlistcomp)? ")" ) |
    ( "[" (testlistcomp)? "]" ) |
    ( "{" (dictorsetmaker)?  "}" ) |
    ( name | number | string+ | "..." | "None" | "True" | "False" )
trailer ::= "(" (arglist)? ")" | "[" subscriptlist "]" | "." name
testlistcomp ::= namedexprtest "," (namedexprtest)* (",")?
trailer ::= "(" (arglist)? ")" | "[" subscriptlist "]" | "." name
subscriptlist ::= subscript ("," subscript)* (",")?
subscript ::= test | (test)? ":" (test)? (sliceop)?
sliceop ::= ":" (test)?
dictorsetmaker ::= 
       ( ((test ":" test | "**" expression) ("," (test ":" test | "**" expression))* (",")?) |
       ( test "," (test)* (",")?) )

namedexprtest ::= test (":= " test)?
test ::= expr (compop expr)*
compop ::= ( "<" | ">" | "==" | ">=" | "<=" | "<>" | "!=" | " in " | " not in " | " is " | " is not " )

classdef ::= "class " name ("(" ws? (arglist)? ws? ")")? ":" suite

suite ::= newline indent statement

arglist ::= argument ("," argument)*  (",")?
argument ::= atomexpr | atomexpr "=" atomexpr
number ::= ([0-9])+ ( ["."] ([0-9])+ )?
string ::= (" " " [^\n]* " " ") | (" ' " [^\n]* " ' ")
indent ::= "\t"
newline ::= "\n"
name ::= [a-zA-Z_] [a-zA-Z_0-9]*
ws ::= ([ \t\n]+)
`)