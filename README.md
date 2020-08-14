# Substance Expressions

Substance Designer Plugin for creating function graphs from code. Includes simple editor and code generating features

## Installation
Just manually add plugin path to search paths in SD Preferences:
https://docs.substance3d.com/sddoc/plugin-search-paths-172825000.html (You need to add path to the root where README.md is located)

After that you shoud see this toolbar with any function graph opened

![Toolbar](https://github.com/igor-elovikov/sd-sex/blob/master/img/toolbar.png)

_(on MacOS created toolbars aren't active by default so you would need to click on IE icon first to see Expression button)_

Alternatively you can install plugin from [release page](https://github.com/igor-elovikov/sd-sex/releases). Just download sex.sdplugin from assets and install it through Plugin Manager in Substance Designer. _Tools -> Plugin Manager_ then hit the button _INSTALL_ and browse the downloaded file.

## Usage

Just click _Expression_ button to open the editor.

![Editor](https://github.com/igor-elovikov/sd-sex/blob/master/img/editor.png)

To create a graph just click _COMPILE_ button. That's it.

When you open the editor the plugin creates a frame object named _Snippet_. Don't delete it as it holds the actual code for the graph. Code will be saved to the snippet object when you hit _COMPILE_ so be careful before you close the editor - even if you're not finished just try to compile it to save.


## The Language
The plugin uses Python AST so it's syntactically Python with the expected results. However it supports a very limited feature set of Python, basically just plain arithmetic and logical expressions and function calls.

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

Note that these are constants declarations, for creating variables use vector functions. 
```python
one = 1.0
two = 2.0

v = float2(one, two) # won't work: float2 accepts constants only
v = vector2(one, two) # OK
```

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

i = get_int("my_int_var")
i2 = get_int2("my_int2_var")
i3 = get_int3("my_int3_var")
i4 = get_int4("my_int4_var")
```

### Samplers
![Samplers](https://github.com/igor-elovikov/sd-sex/blob/master/img/samplers.png)

For sampling use `samplelum(uv, input, filtering)` for grayscale or `samplecol(uv, input, filtering)` for color. 


`samplelum` returns float and `samplecol` returns float4

* `uv` float2 variable for uv coordinates
* `input` integer constant for input number
* `filtering` integer constant for sample. `0` for Nearest and `1` for Bilinear

Note that for input and filtering you have to use explicit constants.
```python
input_num = 5
filter = 0

# This is not supported due to how function graph works. Input and filtering can't be variables
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
v = v1 - v2

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

_Currently it requires some work. It doesn't support consequent operands ie `yes and yes and yes` won't compile. You have to use `(yes and yes) and yes`. Will be fixed in release version_

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

# Logarithm 
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

## Output Value

To mark expression as output value just assign it to special variable __`_OUT_`__
```python
_OUT_ = 10 
```

Just make sure that the type of expression result is the similar as expected type for the graph (if it has one). 

## Type Checking

Type checking is similar to SD which means __no implicit conversion__

```python
x = 1.0 + 2 # Adding float and integer values
``` 

The example above won't compile to graph with the error message in console. You have to resolve this with explicit type conversion according to the result type you want

```python
x = toint(1.0) + 2 # OK [x] is integer value 3
x = 1.0 + tofloat(2) # OK [x] is float value 3.0
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
There is a helper function to autodeclare all graph inputs. Can be very handy if you have a graph with many inputs.

Say you have graph named `My_Graph` with this example inputs

![Inputs](https://github.com/igor-elovikov/sd-sex/blob/master/img/params.png)

In any function subgraph you can just use this
```python
declare_inputs("My_Graph")

# Now you can use inputs straightaway

pos_with_offset = position + float2(0.5, 0.5)
x = 2.0 if trigger else 0.0

# etc
```

## Importing External Functions

Currently plugin automatically import external function from standart package `function.sbs` which included in SD. All functions from `function.sbs` are available straight away. See (https://github.com/igor-elovikov/sd-sex/blob/master/func_list.md) for all the aliases.

Sometimes when you open the editor you see `function.sbs` opened in your packages. Currently this is the only way to resolve dependencies (load the package). However if your package already have dependency on `function.sbs` it won't happen. So it happens only when working on some graph from scratch.

Also any function graph in your current opened packages imported automatically. So if you have function graphs in your current packages you can use them as functions in your scripts everywhere inside these packages

![Function Example](https://github.com/igor-elovikov/sd-sex/blob/master/img/import_func.png)

```python
x = My_Function() # Use function graph id as function name 
y = Other_Function(x, 2.0) # You can use functions from different packages
_OUT_ = y + 2.0
```

Basically if you need to use some function from other .sbs file just open this file so it's listed in your explorer window. All dependencies will be resolved by SD automatically when you save your package. 

## Plugin Settings

All the settings stored in settings.json located in plugin directory.
There you can set the custom font sizes for editor, use it to adjust editor appearance to your DPI
Also there are additional settings:
* `"tab_spaces": 4` - Number of spaces for tabs in the editor
* `"align_max_nodes": 150` - Compiled graph can be aligned to make a more readable structure. However for complex graphs that can be very slow so it triggers only if number of nodes less than `align_max_nodes` setting (set it to zero if you don't need an aligment)

## Metaprogramming Features

This is a very powerful feature which allows you to write modular and more expressive code. It's based on Jinja template engine: https://jinja.palletsprojects.com/

Essentially all the code you write is Jinja template which expanded before it goes to compiler. So it's like writing a code that write the actual script. It can be a little bit confusing at the beginning but it's actually very easy. Basically it's just a text processing.

To check the generated code just click _View Generated Code_ tab in the editor. Try to switch to it from time to time to see how your code looks like and to make sure your template doesn't have any errors. Every time you switch to this tab plugin tries to expand your template and if there's any errors you see them in console output.

Check the Jinja documentation but to start the best way to understand it is to look at practical examples. 

### Jinja Environment

Jinja is set up with line statement `::` so `{% set x = 2 %}` is identical to `:: set x = 2`. Use anything you prefer

Also the path to any external file is set to package path. So if you have any external source files just put them in the same directory with your .SBS file.

### Examples

These are most common practices for writing expressions. Though you can use any feature included in Jinja it's just something that I found the most useful.

#### For Loops

Loops can be used to emulate arrays
```python
:: for i in range(5)
x{{ i }} = {{ i | float }}
:: endfor

# ---- RESULT ---- #

x0 = 0.0
x1 = 1.0
x2 = 2.0
x3 = 3.0
x4 = 4.0

```

Also very useful to sample neighbour pixels.

Basic 3x3 box blur
```python
size = get_float2("$size")
pos = get_float2("$pos")

total_lum = 0.0

:: for x in range(-1, 2)
:: for y in range(-1, 2)
offset = vector2({{ x | float }}, {{ y | float }})
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
:: endfor
:: endfor

_OUT_ = total_lum / 9.0

# ---- RESULT ---- #

size = get_float2("$size")
pos = get_float2("$pos")

total_lum = 0.0

offset = vector2(-1.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(-1.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(-1.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(0.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(0.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(0.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(1.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(1.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)
offset = vector2(1.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0)

_OUT_ = total_lum / 9.0
```

Be careful with loops and always check the generated code. It's very easy to create a huge graph especially with nested loops. 

#### Template Variables

Let's extend the box blur example to use kernel matrix.

```python
size = get_float2("$size")
pos = get_float2("$pos")

# Gaussian 3x3 kernel
:: set kernel = [(0.0625, 0.125, 0.0625), (0.125, 0.25, 0.125), (0.0625, 0.125, 0.0625)]

total_lum = 0.0

:: for x in range(-1, 2)
:: for y in range(-1, 2)
offset = vector2({{ x | float }}, {{ y | float }})
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * {{ kernel[x + 1][y + 1] }}
:: endfor
:: endfor

_OUT_ = total_lum 

# ---- RESULT ---- #
size = get_float2("$size")
pos = get_float2("$pos")

total_lum = 0.0

offset = vector2(-1.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.0625
offset = vector2(-1.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.125
offset = vector2(-1.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.0625
offset = vector2(0.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.125
offset = vector2(0.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.25
offset = vector2(0.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.125
offset = vector2(1.0, -1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.0625
offset = vector2(1.0, 0.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.125
offset = vector2(1.0, 1.0)
total_lum = total_lum + samplelum(pos + offset / size, 0, 0) * 0.0625

_OUT_ = total_lum 

```

Variables can be also useful where you need to use explicit constants and you want to use the same one in many places.
For example you can create a setting for sample filtering.

```python
# 0 for Nearest and 1 for Bilinear
:: set filter = 1

sample = samplelum(pos, 0, {{ filter }})

# ---- RESULT ---- #

sample = samplelum(pos, 0, 1)
```

#### Macros

Macro is like a function that can help you to reduce code duplication.

Let's say you want to muliply a value by factor but leave it unchanged if factor is zero. Of course you can create a function for that but sometimes it's just easier to write a macro.

```python
:: macro apply_modifier(value, modifier)
{{ value }} = {{ value }} * {{ modifier }} if {{ modifier }} > 0.0 else {{ value }}
:: endmacro

x = 1.0
f = 0.0

{{ apply_modifier("x", "f") }}

# ---- RESULT ---- #

x = 1.0
f = 0.0

x = x * f if f > 0.0 else x
```

In this particular case it's probably easier to do without macros but when operations become more complicated macros are must. Especially when you iterate on code and suddenly decide to make some changes on this kind of operation. With macro you just tweak it in one place and recompile.

#### Importing Macros

You can put often used macros in external file and then import it to your code. It works similarly to Python import.

So for our example above we can put our macro in some file like `macros.sex`. Then we can just import it and use

```python
:: import "macros.sex" as macros

x = 1.0
f = 0.0

{{ macros.apply_modifier("x", "f") }}

# ---- RESULT ---- #

x = 1.0
f = 0.0

x = x * f if f > 0.0 else x
```

Note that `macros.sex` has to be in the same directory as your package

#### Including External File

You can also just include any external file to your snippet. It's literally like a pasting files content to the code.
That can be very useful when you share some code between graphs.

```python
:: inlcude "blur.sex"
```

The generated code would be the content of `blur.sex` file

#### If-Else Blocks

Use If-Else blocks for compile-time branching. One of the examples is creating a template in external file which can be altered by some settings. 

For example we can create a file `color_or_grayscale.sex` with this code
```python
:: if color
_OUT_ = uniform_f4_ab(float4(0.0, 0.0, 0.0, 0.0), float4(1.0, 1.0, 1.0, 1.0))
:: else
_OUT_ = uniform_ab(0.0, 1.0)
:: endif
```

Then in the snippet
```python
:: set color = true
:: include "color_or_grayscale.sex"

# ---- RESULT ---- #

_OUT_ = uniform_f4_ab(float4(0.0, 0.0, 0.0, 0.0), float4(1.0, 1.0, 1.0, 1.0))
```

Depending on the `color` setting we can choose the branch for our code. 
