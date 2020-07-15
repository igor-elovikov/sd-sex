# Substance Expressions

Substance Designer Plugin for creating function graphs from code. Includes simple editor and code generating features

## Installation
Just manually add plugin path to search paths in SD Preferences:
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

_OUT_ = sample
```
## Built-in Function Nodes
### Constant
![Constant](https://github.com/igor-elovikov/sd-sex/blob/master/img/constant.png)

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
i3 = int3(1, 2, 3)
i4 = int4(1, 2, 3, 4)

# String
s = "foo"
```

For vector types all components have to be explicit. So `x = float3(0.0)` won't work, use `x = float3(0.0, 0.0, 0.0)` instead

### Vector
![Vector](https://github.com/igor-elovikov/sd-sex/blob/master/img/vector.png)

#### Constructors
Float vector constructors
```python
one = 1.0
two = 2.0
three = 3.0
four = 4.0
f2 = vector2(1.0, 2.0) # [f2] is float2(1.0, 2.0)
f3 = vector3(vector2(1.0, 2.0), 3.0) # [f3] is float3(1.0, 2.0, 3.0)
f4 = vector4(vector2(1.0, 2.0), vector2(3.0, 4.0)) # [f4] is float4(1.0, 2.0, 3.0, 4.0)
```
Built-in constructors are little bit cumbersome for float3 and float4. For those variables you can use merge_float from function.sbs (standart funtions included in SD) instead.
```python
f3 = merge_float3(one, two, three) # much better than vector3((vector2(1.0, 2.0), 3.0)
f4 = merge_float4(one, two, three, four)
```

#### Swizzling
Swizzling works differently for integer and float types. Components for float vector are `.xyzw` and for integer `.abcd`
```python
int_vector = int4(1, 2, 3, 4)
i = int_vector.ab # [i] is int2(1,2)
i = int_vector.aaa # [i] is int3(1, 1, 1)
i = int_vector.dbb # [i] is int3(3, 2, 2)

f_vector = float4(1.0, 2.0, 3.0, 4.0)
f = f_vector.zyx # [f] is float3(3.0, 2.0, 1.0)
f = f_vector.ww # [f] is float2(4.0, 4.0)

# etc
```
Currently swizzling is supported only as rvalue. So assigning to attributes aren't possible
```python
f3 = float3(1.0, 2.0, 3.0)

f3.x = 0.0 # this is not supported!

f3 = merge_float3(0.0, f3.y, f3.z) # use this instead
```

### Variables
![Variables](https://github.com/igor-elovikov/sd-sex/blob/master/img/variables.png)

This one is pretty straightforward
```python
b = get_bool("my_boolean_var")

f = get_float("my_float_var")
f2 = get_float2("my_float2_var")
f3 = get_float3("my_float3_var")
f4 = get_float4("my_float4_var")

i = get_float("my_int_var")
i2 = get_float2("my_int2_var")
i3 = get_float3("my_int3_var")
i4 = get_float4("my_int4_var")
```

### Samplers
![Samplers](https://github.com/igor-elovikov/sd-sex/blob/master/img/samplers.png)

For sampling use `samplelum(uv, input, filtering)` for grayscale or `samplecol(uv, input, filtering)` for grayscale. 


`samplelum` returns float and `samplecol` returns float4

* `uv` float2 variable for uv coordinates
* `input` integer constant for input number
* `filtering` integer constant for sample. `0` for Nearest and `1` for Bilinear

Note that for input and filtering you have to use explicit constants.
```python
input_num = 5
filter = 0

# This is not supported due to how function graph works. Input and filtering can't be mutable
s = samplecol(float2(0.5, 0.5), input_num, filter) # won't work

s = samplecol(float2(0.5, 0.5), 5, 0) # OK
```


### Cast
![Cast](https://github.com/igor-elovikov/sd-sex/blob/master/img/cast.png)

Casting for the same size vectors. SD supports casting from int to float and vice versa. 
```python
# To float casts functions: tofloat(), tofloat2(), tofloat3(), tofloat4()
# To int casts functions: toint(), toint2(), toint3(), toint4()

i = 2
f = tofloat(i) # [f] is 2.0

f3 = float3(1.0, 2.0, 3.0)
i3 = toint3(f3) # [i3] id int3(1, 2, 3)
```

### Operator
![Operator](https://github.com/igor-elovikov/sd-sex/blob/master/img/operator.png)

Like in SD operators work with the same size and the same type variables.

```python
v1 = float3(1.0, 2.0, 3.0)
v2 = float3(1.0, 2.0, 3.0)

# Add
v = v1 + v2

# Subtraction
v = v1 + v2

# Negation
v = -v1

# Division (per component)
v = v1 / v2

# Multiplication (per component)
v = v1 * v2

# Modulo (per component)
v = v1 % v2

# Scalar multiplication (only float)
# The notation is [vector] @ [scalar] with the exact order so scalar always on the right side
v = v1 @ 2.0 # [v] is float3(2.0, 4.0, 6.0)

# Dot product
v = v1 ^ v2
# or
v = dot(v1, v2)
```

All arithmetical and logical expressions follows Python grammar rules so you're not limited to just one operator
```python
v = (v1 + v2 @ 2.0) * float3(5.0, 5.0, 5.0) - (v2 - v1) @ 5.0 
```

### Logical
![Logical](https://github.com/igor-elovikov/sd-sex/blob/master/img/logical.png)

Logical operators are similar to Python
```python
yes = True
no = False

b = yes and no # False
b = yes or no # True
b = not yes # False
```

### Comparison
![Comparison](https://github.com/igor-elovikov/sd-sex/blob/master/img/comparison.png)

Comparison operators are similar to Python
```python
one = 1.0
two = 2.0
four = 4

is_even = four % 2 == 0 # True
b = one > two # False
b = four <= 4 # True
b = four != 4 # False
# etc
```

### Conditional
![Control](https://github.com/igor-elovikov/sd-sex/blob/master/img/control.png)

SD basically supports only ternary operator for conditional control. The plugin currently goes with the same limitation so there is no actual branching expressions.

Conditional expression
```python
b = True
f = 2.0
x = 5.0 if b else 0.0 # [x] is 5.0
x = 5.0 if not b else 0.0 # [x] is 0.0
x = 5.0 if b and (f * 3.0) < 4.0 else 0.0 # you can use any logical expression in condition
```

Hovewer you can still do branching it's just not so convenient. Usually you just calculate all branches (all values for the result) and then choose the appropriate by conditional expression
```python

branch1 = # ... calculate branch 1 ... #

branch2 = # ... calculate branch 2 ... #

condition = trigger > 0

result = branch1 if condition else branch2
```

Emulating switch expression
```python
switch = 3

x = 0.0
x = 1.0 if switch == 1 else x
x = 2.0 if switch == 2 else x
x = 3.0 if switch == 3 else x
x = 4.0 if switch == 4 else x

# Here [x] is 3.0
```

### Function
![Function](https://github.com/igor-elovikov/sd-sex/blob/master/img/function.png)

All SD built-in functions are supported. All functions except `min`, `max`, `abs` accept only float arguments. Most of the function work with scalar and vector types. If function accepts vector it performs per component operation (exactly like SD)
```python
v1 = float4(1.0, 2.0, 3.0, 4.0)
v2 = float4(5.0, 6.0, 7.0, 8.0)
t = 0.5

# 2Pow
x = pow2(v1)

# Absolute
x = abs(v1)

# Arc Tangent 2 - only float2 argument
x = atan2(v1.xy)

# Cartesian - only 2 float scalar arguments 
x = cartesian(v1.x, v1.y)

# Ceil
x = ceil(v1)

# Cosine
x = cos(v1)

# Exponential
x = exp(v1)

# Floor
x = floor(v1)

# Linear Interpolation - last argument is float scalar
x = lerp(v1, v2, t)

# Logarithm - this is a natural logarithm (ln x) SD doesn't say that explicitly
x = log(v1)

# Logarithm base 2
x = log2(v1)

# Maximum
x = max(v1, v2)
x = max(2, 5) # also supports integer types

# Minimum
x = min(v1, v2)

# Random - only scalar float arguments
x = rand(1.0) # [x] is random between 0 and 1.0

# Sine
x = sin(v1)

# Square Root
x = sqrt(v1)

# Tangent
x = tan(v1)
```


## Exporting Variables
For FX-Maps SD allows you to use Set/Sequence nodes to output more than one value. See https://docs.substance3d.com/sddoc/using-the-set-sequence-nodes-102400025.html

The plugin also supports this by `export` keyword. Basically you can export any variable in your script to use it later in other function graphs. Just make sure they are evaluated after exporting. As documentation said the usual workflow is to create uber function in top parameter ("Color/Luminocity" for example) and export all the variables there.

 Exporting works like this
 ```python
 # some function on top level parameters
 x = 1.0
 y = 10.0 * some_value
 
 vec = vector2(x, y)
 
 export(vec)
 
 _OUT_ = 1.0
 
 ```

In other function you just get exported variable
```python
# some function evaluated later

vec = get_float2("vec") # be careful: you have to use the correct type getter (float2 in this case)
```

## Declaring Graph Inputs
## Importing External Functions
## Plugin Settings
## Metaprogramming Features
