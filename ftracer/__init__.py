#!/usr/bin/env python3
#
# Decorator functions to trace invocation of functions and class methods.
# Copyright (c) 2024, Hiroyuki Ohsaki.
# All rights reserved.
#

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import sys
import types

DEBUG = False
PREFIX = '** '
LIST_LIMIT = 80

def __debug(msg):
    print(f'{PREFIX}{msg}', file=sys.stderr)

def __repr(v):
    """Pretty printer for object V."""
    name = type(v).__name__
    if name == 'str':
        return f"'{v}'"
    elif name == 'NoneType':
        return 'None'
    elif name == 'float':
        return f'{v:.2f}'
    elif name == 'list':
        elems = []
        length = 0
        for elem in v:
            s = __repr(elem)
            elems.append(s)
            length += len(s)
            if length > LIST_LIMIT:
                elems.append('...')
                break
        elems_str = ', '.join(elems)
        return f'[{elems_str}]'
    elif name in ['int', 'dict', 'type']:
        return f'{v}'
    elif name in ['function']:
        s = f'{v}'
        s = re.sub(r' at 0x[0-9a-f]+', '', s)
        return s
    else:
        return name

def trace(func):
    """Decorator function for a function for watching its invocation."""
    def __wrapper(*args, **kwargs):
        args_list = [
            f'{k}={__repr(v)}' for k, v in zip(func.__code__.co_varnames, args)
        ]
        kwargs_list = [f'{k}={__repr(v)}' for k, v in kwargs.items()]
        all_args = ', '.join(args_list + kwargs_list)
        __debug(f'{func.__name__}({all_args})')
        retval = func(*args, **kwargs)
        # __debug(f'{func.__name__}({all_args}) -> {__repr(retval)}')
        return retval

    return __wrapper

def trace_methods(cls):
    """Decorator function for a class for watching invocations of all
    methods."""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('__'):
            setattr(cls, attr_name, trace(attr))
    return cls

def trace_all_functions(decorator=None, module='__main__'):
    """Install decorator function DECORATOR to all functions in the module
    MODULE.  If DECORATOR is not specified, use `trace' decorator.  If MODULE
    is not specified, use the main module `__main__'."""
    if decorator is None:
        decorator = trace
    global_vars = sys.modules[module].__dict__
    for name, obj in global_vars.items():
        if isinstance(obj, types.FunctionType) and obj.__module__ == module:
            if not obj.__name__.startswith('__'):
                if DEBUG:
                    __debug(f'attach {__repr(decorator)} to function {name}')
                global_vars[name] = decorator(obj)

def trace_all_classes(decorator=None, module='__main__'):
    """Install decorator function DECORATOR to all classes in the module
    MODULE.  If DECORATOR is not specified, use `trace_methods' decorator.  If
    MODULE is not specified, use the main module `__main__'."""
    if decorator is None:
        decorator = trace_methods
    global_vars = sys.modules[module].__dict__
    for name, obj in global_vars.items():
        if isinstance(obj, type) and obj.__module__ == module:
            if not obj.__name__.startswith('__'):
                if DEBUG:
                    __debug(f'attach {__repr(decorator)} to class {name}')
                global_vars[name] = decorator(obj)
