from __future__ import print_function, absolute_import
import re

from .Globals import print1, print2, print3, is_num, value_type
from . import Globals
from . import Runtime
from . import Exceptions

def get_classes(key, scope):
    from . import Calc
    if type(key) is not tuple:
        n = value_type(key)
        if 'Error' == n:
            k = re.findall('^\s*([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*$', str(key))
            if k:

                ###############NOT SURE IF PREDEFINED FUNC MAKES ANY DIFFERENCE########
                #if k[0][0] in Globals.predefined_funcs:
                #    return 'predef'
               #return Globals.functions[k[0][0]][0]

                #returns the calculated value from function
                return Calc.pass_to_func(k[0], scope), None
            else:
                #returns both value and memory location
                return Runtime.get_key_first(key, scope)
        else:
            return n, None
    #The below 'if' condition will never be used, not sure about the else condition, but couldn't find the use case
    if len(key) != 1:
        t = Globals.in_var_table(key[0], scope)
        if t:
            return Globals.var_table[t],t
    else:
        if key in Globals.memory:
            return Globals.memory[key][0].type[0]
        else:
            raise Exceptions.any_user_error("Invalid Memory location", key)


def get_val(key, scope, mul = 1):
    from . import Calc

    if type(key) is not tuple:
        n = is_num(key)
        if 'Error' == n:
            k = re.findall('^\s*([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*$', key)
            if k:
                if mul != 1:
                    return 0
                val = Calc.pass_to_func(k[0], scope)
                return val
            else:
                if mul == 1:
                    key = Runtime.get_key(key, scope)
                else:
                    key = Runtime.get_key_first(key, scope)
                if type(key) is int:
                    return key
        else:
            return eval(str(key))
    if len(key) != 1:
        t = Globals.in_var_table(key[0], scope)
        if t:
            if mul != 1:
                if Globals.var_table[t].cast != 0:
                    return 0
            ret = Globals.var_table[t].val
            if ret == '':
                raise Exceptions.any_user_error("Variable " + key[0] + " used "
                        "without initialisation in current line.")
            return Globals.var_table[t].val
        else:
            raise Exceptions.any_user_error("Invalid variable used in current line.")
    else:
        if key in Globals.memory:
            if mul != 1:
                if Globals.memory[key][0].type[1] != 0:
                    return 0
            return Globals.memory[key][0].v
        else:
            raise Exceptions.any_user_error("Invalid Memory location", key)

get_val = Globals.analyze(get_val)

def set_val(key, val, scope = '-none-'):

    if type(key) is not tuple:
        if scope == '-none-':
            raise Exceptions.any_user_error("Something wrong.")
        if is_num(key) == 'Error':
            key = Runtime.get_key(key, scope)
        else:
            raise Exceptions.any_user_error("Trying to assign value to a non-variable")

    if len(key) != 1:
        Globals.gui += "\nupdate_variable(\'"+'-'.join(key[1].split())+ \
            "-"+key[0]+"\',\'"+str(val)+"\');"

        t = Globals.in_var_table(key[0], scope)
        if t:
            Globals.var_table[t].setval(val)
    else:
        Globals.gui += "\nupdate_variable(\'"+str(key[0])+"\',\'"+str(val)+"\');"

        if key in Globals.memory:
            Globals.memory[key][0].v = val
        else:
            raise Exceptions.any_user_error("Invalid Memory location set_val", key)

set_val = Globals.analyze(set_val)