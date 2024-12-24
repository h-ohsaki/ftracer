#!/usr/bin/env python3
#
#
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

PREFIX = '**ftracer: '
LIST_LIMIT = 30

def __debug(msg):
    print(f'{PREFIX}{msg}', file=sys.stderr)

def __repr(v):
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
    def __wrapper(*args, **kwargs):
        args_list = [
            f'{k}={__repr(v)}' for k, v in zip(func.__code__.co_varnames, args)
        ]
        kwargs_list = [f'{k}={__repr(v)}' for k, v in kwargs.items()]
        all_args = ', '.join(args_list + kwargs_list)
        __debug(f'{func.__name__}({all_args})')
        retval = func(*args, **kwargs)
        __debug(f'{func.__name__}({all_args}) -> {__repr(retval)}')
        return retval

    return __wrapper

def trace_methods(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('__'):
            setattr(cls, attr_name, trace(attr))
    return cls

def trace_all_functions(decorator=None):
    if decorator is None:
        decorator = trace
    global_vars = globals()
    for name, obj in global_vars.items():
        if isinstance(obj, types.FunctionType) and obj.__module__ == __name__:
            if not obj.__name__.startswith('__'):
                __debug(f'attach {__repr(decorator)} to function {name}')
                global_vars[name] = decorator(obj)

def trace_all_classes(decorator=None):
    if decorator is None:
        decorator = trace_methods
    global_vars = globals()
    for name, obj in global_vars.items():
        if isinstance(obj, type) and obj.__module__ == __name__:
            if not obj.__name__.startswith('__'):
                __debug(f'attach {__repr(decorator)} to class {name}')
                global_vars[name] = decorator(obj)

class _TestClass:
    def m1(self, x, y):
        return x + y

    def m2(self, z):
        return z * z

def _f1(x):
    _f2(x + 1)

def _f2(y):
    return _f3(y * 2, 3)

def _f3(x, y):
    return x + y

def _f4(name, age):
    pass

def _f5(lst, x):
    pass

def _f6(lst, x):
    pass

def _f7(x, y):
    pass

def main():
    trace_all_functions()
    trace_all_classes()

    _f1(4)
    _f2(12.3456789)
    _f4('John', 34)
    _f5(list(range(1000)), 1 / 123456789)
    _f5([1, '2', 3.4, str, _f5], None)
    _f6([1, '2', 3.4, str, _f5], None)
    _f7(3, 'soo')

    obj = _TestClass()
    obj.m1(1.2, 3.4)
    obj.m2(11)

if __name__ == "__main__":
    main()
