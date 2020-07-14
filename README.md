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

### Types
All function graph types are supported
```python
# Boolean
a = True
b = False

# Float 
f = 0.0
f2 = float2(1.0, 2.0)
f3 = float3(1.0, 2.0, 3.0)
f4 = float4(1.0, 2.0, 3.0, 4.0)

# Integer
i = 2
i2 = int2(1, 2)
i2 = int3(1, 2)
i2 = int4(1, 2)

# String
s = "foo"
```

## Importing External Functions
## Metaprogramming Features
