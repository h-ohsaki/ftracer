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

import inspect
import re
import sys
import threading
import types

import ansiterm

DEBUG = True
PREFIX = ''
LIST_LIMIT = 40

def _debug(msg):
    print(f'{PREFIX}{msg}', file=sys.stderr)

def _repr(v):
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
            s = _repr(elem)
            elems.append(s)
            length += len(s)
            if length > LIST_LIMIT:
                elems.append('...')
                break
        elems_str = ', '.join(elems)
        return f'[{elems_str}]'
    elif name in ['int', 'dict', 'type']:
        return f'{v}'
    elif name in ['function', 'method']:
        s = f'{v}'
        s = re.sub(r' of <.+?>', '', s)
        s = re.sub(r' at 0x[0-9a-f]+', '', s)
        return s
    else:
        # s = f'{v}'
        # s = re.sub(r' object', '', s)
        # s = re.sub(r' at 0x[0-9a-f]+', '', s)
        # return s
        return name

_call_depth = threading.local()
_call_depth.value = 0

def _var_names(func, size):
    try:
        return func.__code__.co_varnames
    except AttributeError:
        return ['??'] * size

def trace(func):
    """Decorator function for a function for watching its invocation."""
    def _wrapper(*args, **kwargs):
        _call_depth.value += 1
        # Function might have been wrapped by another decorator.
        orig_func = func.__wrapped__ if hasattr(func, '__wrapped__') else func
        # Constrct function arguments.
        args_list = [
            f'{k}={_repr(v)}' for k, v in zip(_var_names(orig_func, len(args)), args)
        ]
        kwargs_list = [f'{k}={_repr(v)}' for k, v in kwargs.items()]
        all_args = ', '.join(args_list + kwargs_list)
        # Display trace event.
        indent = '  ' * (_call_depth.value - 1)
        name_str = ansiterm.cyan(orig_func.__name__)
        args_str = ansiterm.magenta(all_args)
        _debug(f'{indent}{name_str}({args_str})')
        retval = func(*args, **kwargs)
        retval_str = ansiterm.blue(_repr(retval))
        _debug(f'{indent}-> {retval_str}')
        _call_depth.value -= 1
        return retval

    return _wrapper

def _is_method_from_base(cls, method_name):
    for base in cls.__mro__[1:]:
        if hasattr(base, method_name):
            base_method = getattr(base, method_name)
            if inspect.isfunction(base_method) or inspect.ismethod(
                    base_method):
                return True
    return False

def trace_methods(cls):
    """Decorator function for a class for watching invocations of all
    methods."""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith(
                '_') and not _is_method_from_base(cls, attr.__name__):
            if DEBUG:
                _debug(f'[INFO] attach method: {cls}.{attr_name}')
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
            if not obj.__name__.startswith('_'):
                if DEBUG:
                    _debug(f'[INFO] attach function: {name}')
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
            if not obj.__name__.startswith('_'):
                if DEBUG:
                    _debug(f'[INFO] attach class: {name}')
                global_vars[name] = decorator(obj)
