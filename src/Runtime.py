import re
import globals
from globals import Value
import Calc
import i_o
import groups
import Vars
import sys
import Exceptions


def makeMemory(mem, indices, l, type):
    mem = (mem, )
    step = globals.size_of[type if l == 0 else 'pointer']
    globals.memory[mem][0].v = malloc(indices[0] if indices else 1, step, l)
    if indices[1:]:
        for i in range(0, indices[0]):
            makeMemory(globals.memory[mem][0].v + i*step, indices[1:], l-1, type)


def decl(var, val, cast, scope):
    pointers = re.findall('\*+', var)
    if pointers:
        level = len(pointers[0])
        var = re.sub('\*', '', var)
    else:
        level = 0
    data = globals.get_details(var)
    var = data[0]
    indices = data[1]
    indices = [Calc.calculate(ind, scope) for ind in indices]
    level += len(indices)
    key = globals.in_var_table(var, scope)
    if key and key[1] == scope:
        raise Exceptions.any_user_error("Error 101: Multiple declaration of variable " + var + "\n")
    newKey = (var, scope, globals.curr_mem)
    globals.var_table[newKey] = [Value(val), cast, level, globals.curr_mem]
    if level:
        size = globals.size_of['pointer']
    else:
        size = globals.size_of[cast]
    globals.memory[(globals.curr_mem,)] = [globals.var_table[newKey][0], size, level+1]
    if level == 0:
        globals.curr_mem += globals.size_of[cast]
    else:
        globals.curr_mem += globals.size_of['pointer']
    if indices:
        makeMemory(globals.curr_mem - globals.size_of['pointer'], indices, level - 1, cast)


def get_key(var, scope):
    var = globals.get_details(var)
    name = var[0]
    indices = var[1]
    if indices:
        indices = [Calc.calculate(ind, scope) for ind in indices]
        key = globals.in_var_table(name, scope)
        return resolve(key, indices)
    else:
        name = name.decode('string_escape')
        if re.match(r"'.'", name):
            return ord(name.replace("'", ''))
        return globals.in_var_table(name, scope)


def resolve(key, indices):
    k = key
    while indices:
        k = (Vars.get_val(k),)
        k = (k[0] + globals.memory[k][1]*indices[0], )
        indices.pop(0)
    return k


def chk_decl(line, scope):
    r = re.findall(
        r'^(?s)\s*(long\s+double|long\s+long\s+int|long\s+long|long\s+int|long|int|float|double|char)\s+'
        '((\s*\**\s*[a-zA-Z_]+[a-zA-Z0-9_]*(\[.*\])*)(\s*=\s*(.*?))?\s*,)*((\s*\**\s*[a-zA-Z_]+[a-zA-Z0-9_]*(\[.*\])*)(\s*=\s*(.*?))?\s*;)',
        line)
    if len(r) != 0:
        r = r[0]
        cast = r[0]
        a = re.sub(cast, '', line)
        a = re.sub(';', '', a)
        a = globals.toplevelsplit(a, ',')
        #a = a.split(',')
        a = [k.strip().split('=') for k in a]
        for variables in a:
            if len(variables) == 1:
                decl(variables[0].strip(), '', cast, scope)
            else:
                decl(variables[0].strip(), Calc.calculate(variables[1], scope, globals.var_table), cast, scope)
        return True
    else:
        return False


#def update(var, val, scope):
    #key = globals.in_var_table(var, scope)
    #if key:
        #globals.var_table[key][0].v = val
    #else:
        #print('Error 103: ' + var + "not declared \n")
        #return


def is_updation(exp):
    k = re.match(r'^(?s)\s*[a-zA-Z_]+[a-zA-Z0-9_]*\s*=.*;', exp)
    return 1 if k else 0


def garbage_collector(scope):
    keys = globals.var_table.keys()
    for key in keys:
        if key[1] == scope:
            del globals.var_table[key]
            del globals.memory[(key[2],)]
    return


def halter(line):
    if re.match(r'^(?s)\s*break\s*;', line):
        raise Exceptions.custom_break;
    if re.match(r'^(?s)\s*continue\s*;', line):
        raise Exceptions.custom_continue;

def run_through(code, num):
    i = num
    while i < len(code):
        line = code[i]
        i += 1
        if type(line) != str:
            continue
        k = re.findall(r'^(?s)\s*(long\s+double|long\s+long\s+int|long\s+long|long\s+int|long|int|float|double|char)\s+'
                       '([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*$', line)
        if k:
            assert len(k) == 1
            k = k[0]
            params = [a.strip() for a in k[2].split(',')]
            for index, par in enumerate(params):
                for data_type in globals.data_types:
                    if par.startswith(data_type):
                        rep = re.sub(data_type + r'\s*', '', par)
                        params[index] = (data_type, rep)
                        break
            if len(params[0]) > 0:
                type_key = tuple([temp[0] for temp in params])
            else:
                type_key = ''
            if k[1] in globals.functions and globals.functions[k[1]][2] == '' \
                    and globals.functions[k[1]][3] == type_key:
                globals.functions[k[1]] = [k[0], params, code[i], type_key]


def decl_func(line):
    k = re.findall(r'^(?s)\s*(long\s+double|long\s+long\s+int|long\s+long|long\s+int|long|int|float|double|char)\s+'
                   '([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*;\s*$', line)
    if k:
        assert len(k) == 1
        k = k[0]
        params = [a.strip() for a in k[2].split(',')]
        for index, par in enumerate(params):
            for data_type in globals.data_types:
                if par.startswith(data_type):
                    rep = re.sub(data_type + r'\s*', '', par)
                    params[index] = (data_type, rep)
                    break
        if len(params[0]) > 0:
            type_key = tuple([temp[0] for temp in params])
        else:
            type_key = ''
        if k[1] in globals.functions:
            print "Error!! Multiple declaration of function\n"
        else:
            globals.functions[k[1]] = [k[0], params, '', type_key]
        return 1
    else:
        return 0


def def_func(line, code, num):
    k = re.findall(r'^(?s)\s*(long\s+double|long\s+long\s+int|long\s+long|long\s+int|long|int|float|double|char|void)\s+'
                   '([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*$', line)
    if k:
        assert len(k) == 1
        k = k[0]
        params = [a.strip() for a in k[2].split(',')]
        for index, par in enumerate(params):
            for data_type in globals.data_types:
                if par.startswith(data_type):
                    rep = re.sub(data_type + r'\s*', '', par)
                    params[index] = (data_type, rep)
                    break
        if len(params[0]) > 0:
            type_key = tuple([temp[0] for temp in params])
        else:
            type_key = ''
        if k[1] == 'main':
            run_through(code, num + 1)
            execute(code[num], 'global')
            raise Exceptions.main_executed()
        if k[1] in globals.functions and (globals.functions[k[1]][2] != '' or globals.functions[k[1]][3] != type_key):
            raise Exceptions.any_user_error("Error!! Multiple declaration of function")
        else:
            globals.functions[k[1]] = [k[0], params, code[num], type_key]
        return 1
    elif decl_func(line):
        return 1
    else:
        return 0


def traverse(code, scope):
    i = 0
    while i < len(code):
        line = code[i]
        i += 1
        if type(line) is not str:
            continue
        if len(line) < 1:
            continue
        if chk_decl(line, scope):
            continue
        if is_updation(line):
            Calc.calculate(line, scope, globals.var_table)
            continue
        if def_func(line, code, i):
            continue


def malloc(num, step, level):
    assert level >= 0
    ret = globals.curr_mem
    for i in range(0, num):
        globals.memory[(globals.curr_mem,)] = [Value(''), step, level + 1]
        globals.curr_mem += step
    return ret


def execute(code, scope):
    if type(code) is str:
        r = execute([code], scope)
        if r is not None:
            garbage_collector(scope)
            return r
    i = 0
    r = groups.if_conditionals(code, scope)
    if r is not "NO":
        return r
    r = groups.if_for(code, scope)
    if r is not "NO":
        return r
    r = groups.if_while(code, scope)
    if r is not "NO":
        return r
    r = groups.if_do_while(code, scope)
    if r is not "NO":
        return r
    while i < len(code):
        line = code[i]
        i += 1
        if type(line) is list:
            r = execute(line, scope + " " + str(i - 1))
            if r is not None:
                garbage_collector(scope)
                return r
            continue
        if len(line) < 1:
            continue
        if chk_decl(line, scope):
            continue
        if i_o.handle_input(line, scope):
            continue
        if i_o.handle_output(line, scope):
            continue
        if is_updation(line):
            Calc.calculate(line, scope, globals.var_table)
            continue
        if halter(line):
            continue
        ret = re.findall(r'^\s*return\s+(.*)\s*;\s*$', line);
        if ret:
            ret = Calc.calculate(ret[0], scope)
            garbage_collector(scope)
            return ret
        Calc.calculate(line, scope, globals.var_table)
    garbage_collector(scope)