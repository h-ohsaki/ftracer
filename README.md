# ftracer Package

ftracer - decorator functions to trace invocation of functions and class methods

## DESCRIPTION

A Python module for tracing function and method invocations with detailed,
customizable logging. The `ftracer` module provides tools for decorating
individual functions, all functions in a module, and all methods in a class to
log their invocation, arguments, and return values. This is particularly
useful for debugging and understanding the flow of execution in your code.

`ftracer` allows developers to:
- Decorate individual functions with the `@trace` decorator to log their
  calls.
- Decorate entire classes with the `@trace_methods` decorator to trace all
  method calls within a class.
- Automatically attach decorators to all functions or classes in a module
  using `trace_all_functions` and `trace_all_classes`.
- Customize the tracing behavior, such as pretty-printing arguments and
  limiting list representations.

Key features:
- Customizable pretty-printer for function arguments and return values.
- Ability to apply tracing globally to all functions or classes in a module.
- Optional debug mode for additional trace logs.

---

## EXAMPLE

### Tracing Individual Functions

``` python
from ftracer import trace

@trace
def add(a, b):
    return a + b

result = add(5, 3)
```

```
** add(a=5, b=3)
```

### Tracing All Methods in a Class

``` python
from ftracer import trace_methods

@trace_methods
class Calculator:
    def multiply(self, x, y):
        return x * y

calc = Calculator()
calc.multiply(4, 7)
```

```
** multiply(self=<Calculator>, x=4, y=7)
```

### Applying Traces Globally in a Module

``` python
from ftracer import trace_all_functions

trace_all_functions()

def greet(name):
    return f"Hello, {name}!"

greet("Alice")
```

```
** greet(name='Alice')
```

# INSTALLATION

``` sh
pip3 install ftracer
```

# AVAILABILITY

The latest version of `ftracer` module is available at
PyPI (https://pypi.org/project/ftracer/) .

# SEE ALSO

- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)

# AUTHOR

Hiroyuki Ohsaki <ohsaki[atmark]lsnl.jp>
