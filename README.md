# Substance Expressions

Substance Designer Plugin for creating function graphs from code. Includes simple code editor and code generating features

## Installation
Just manually add plugin path to search paths in SD Prefernces:
https://docs.substance3d.com/sddoc/plugin-search-paths-172825000.html
## The Language
The plugin uses Python AST so it's syntactically Python with the expected results. However it supports a very limited featureset of Python, basically just plain arithmetic and logical expressions and function calls.

It looks like this:
```python
# This is one line comment

x = 1.0 # assign float value 1.0 to variable [x]
y = 0.5
pos = get_float2("$pos") # get system variable $pos for pixel processor

sample = samplelum(pos + vector2(x, y), 0, 0) # sample pixel 
```

### Variables
## Importing External Functions
## Metaprogramming Features
