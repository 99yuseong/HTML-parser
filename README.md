# HTML Parser

This HTML parser is an SLR parser implemented in Python (strict HTML)

This project was produced as final project of GIST's EC3204 lecture 'Programming Language and Compilers' in Fall sememster of 2022.

## Usage

```python
# Setting
from HTML import HTML

html = HTML("source.txt") # input html source.txt 

# Getting a Dom
html.print_dom_tree("output.txt") # output Dom tree at output.txt

# Search
search_all = html.search(['div', 'class', 'value'])
    # input [ tag_name, attr_name, attr_value ]
    # return [ <div class="value">, <div class="value">, <div class="value">, ... ]

get_text_all = html.search_all(['div', 'class', 'value'])
    # input [ tag_name, attr_name, attr_value ]
    # return [ "text_node_1", "text_node_2", "text_node_3", ... ]

```

## Error log
If the source.txt has token Error or Syntax Error, Error log will be printed at terminal. you can check the details in log

### Tokenizing Error
```
Token Error : '<' is not tokenizable
    <<title>...
    ^
```
### Parsing Error
You can see all Syntax Error messages in [Here](#syntax-error)
```  
Syntax Error : There should be attribute value after '='
    <meta c=charset="utf-8">
            ^
```

## Performance
Compare the time simple search for tag and get texts
```
Beautiful Soup   : 0.037s
This HTML parser : 0.126s
```


## Token

```python
class Token(NamedTuple):
    type: str     # token type
    value: str    # token value
    t_no: int     # token no
```

## Tokenizing

```python
# 1st-tokenizing
| opening_tag
| closing_tag
| text_node

# 2nd-tokenizing(for opening_tag)
| variable    # tag_name, attr_name
| value       # attr_value
| symbol      # !, <, >, =, /
```

## Parsing
This HTML parser used SLR(1) Grammer

### Parsing Rules
|Reduce Rule|Tag Grammer|
|-|-|
|R0 |S -> S'|
|R1 |S' -> E|
|R2 |S' -> E/|
|R3 |S' -> /T|
|R4 |E -> T|
|R5 |E -> TA|
|R6 |A -> AB|
|R7 |A -> B |
|R8 |B -> C |
|R9 |B -> C=a|
|R10|C -> v|
|R11|T -> v|

||expression|
|-|-|
|S |start|
|S'|expr|
|E |expr without '/'|
|T |tag_name|
|A |attributes|
|B |attribute|
|C |attribute_name|
|a |attribute_value, string which denoted by "(string)"|
|v |variable, string with digit, alphabet and symbols such as '_', '-', ':'|

### Syntax Error
||Syntax Error|
|-|-|
|E0 |There should be tag name after '<' or '</'|
|E1 |There is no tag name|
|E2 |Tag should end with only one '/'|
|E3 |Tag should be end '>' or '/>'|
|E4 |Attribute can not exist after '/'|
|E5 |There is no variable before '='|
|E6 |Attribute value can not used alone|
|E7 |Closing tag should end '>'|
|E8 |Attribute can not exist in closing tag|
|E9 |There should be '=' between attribute name and value|
|E10|There should be attribute value after '='|
|E11|'==' is not defined symbol|

### SLR(1) Parsing Table
||/|=|v|a|$|S'|E|T|A|B|C|
|-|-|-|-|-|-|-|-|-|-|-|-|
|0 |S4 |E0 |S14|E0 |E1 |1 |2 |6 |  |  |  |
|1 |E2 |E3 |E4 |E4 |R0 |  |  |  |  |  |  |
|2 |S3 |E5 |E4 |E6 |R1 |  |  |  |  |  |  |
|3 |E2 |E3 |E4 |E4 |R2 |  |  |  |  |  |  |
|4 |E0 |E0 |S14|E0 |E1 |  |  |5 |  |  |  |
|5 |E7 |E7 |E8 |E8 |R3 |  |  |  |  |  |  |
|6 |R4 |E1 |S13|E6 |R4 |  |  |  |7 |9 |10|
|7 |R5 |E5 |S13|E6 |R5 |  |  |  |  |8 |10|
|8 |R6 |E5 |R6 |E6 |R6 |  |  |  |  |  |  |
|9 |R7 |E5 |R7 |E6 |R7 |  |  |  |  |  |  |
|10|R8 |S11|R8 |E9 |R8 |  |  |  |  |  |  |
|11|E10|E11|E10|S12|E10|  |  |  |  |  |  |
|12|R9 |E5 |R9 |E6 |R9 |  |  |  |  |  |  |
|13|R10|R10|R10|E9 |R10|  |  |  |  |  |  |
|14|R11|E5 |R11|E6 |R11|  |  |  |  |  |  |
