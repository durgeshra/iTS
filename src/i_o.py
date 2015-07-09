from globals import print1, print2, print3
import globals
import Exceptions
import re
import sys
import Calc
import Vars


def var_types(s):
    s = globals.toplevelsplit(s, ' ')
    for i in range(0,len(s)):
        if s[i] is '':
            continue
        s[i] = re.sub(r'%', '', s[i])
        if re.findall(r'.*lld', s[i]):
            t = re.sub(r'lld', '',s[i])
            s[i] = ('long long', 696969 if t is '' else int(t))
        elif re.findall(r'.*ld', s[i]):
            t = re.sub(r'ld', '',s[i])
            s[i] = ('long', 696969 if t is '' else int(t))
        elif re.findall(r'.*d', s[i]):
            t = re.sub(r'd', '',s[i])
            s[i] = ('int', 696969 if t is '' else int(t))
        elif re.findall(r'.*c', s[i]):
            t = re.sub(r'c', '',s[i])
            s[i] = ('char', 696969 if t is '' else int(t))
        elif re.findall(r'.*s', s[i]):
            t = re.sub(r's', '',s[i])
            s[i] = ('string', 696969 if t is '' else int(t))
        elif re.findall(r'.*lf', s[i]):
            t = re.sub(r'lf', '',s[i])
            s[i] = ('double', 696969 if t is '' else int(t))
        elif re.findall(r'.*Lf', s[i]):
            t = re.sub(r'Lf', '',s[i])
            s[i] = ('long double', 696969 if t is '' else int(t))
        elif re.findall(r'.*f', s[i]):
            t = re.sub(r'f', '',s[i])
            s[i] = ('float', 696969 if t is '' else int(t))
    print1(s)
    return s



def handle_input(statement, scope):
    # statement is something like scanf("%d %c\n%lld", &a, &b, &c)
    statement = statement.decode('string_escape')
    print2("STATEMENT TO INPUT: ", statement, "WITH SCOPE: ", scope)
    # sep = [('%d %c\n%lld', ' &a, &b,', ' &c')]
    sep = re.findall(r'(?s)scanf\s*\(\s*\"(.*)\"\s*,(.*,)*(.*)\)', statement)
    print2("sep: ", sep)
    if len(sep) == 0:
        return False
    elif len(sep) > 1:
        return Exceptions.any_user_error("I think you might be missing a semicolon")

    print2("Reached here in handle_input")
    variables = globals.toplevelsplit(sep[0][1], ',')
    variables = variables[:-1]
    variables.append(sep[0][2])
    # now, variables = ['&a', '&b', '&c']
    var_type = var_types(sep[0][0])
    reg = re.sub(r'%(lld|ld|d)', '%d', sep[0][0])
    reg = re.sub(r'%(Lf|lf|f)', '%f', reg)
    reg = reg.replace(' ', r'\s+')
    reg = reg.replace('\n', r'\s+')
    reg = reg.replace('\r', r'\s+')
    reg = reg.replace('%d', r'\s*([-+]?\d+)')
    reg = reg.replace('%f', r'\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)')
    reg = reg.replace('%c', r'[\n\r]*(.)')
    reg = reg.replace('%s', r'\s*(\S+)')
    reg = '^{0}'.format(reg)
    values = re.findall(reg, globals.inp)
    globals.inp = re.sub(reg, '', globals.inp)

    print2(variables, reg, values)
    if len(values) == 0:
        return False

    if type(values[0]) is str:
        values = [[ values[0] ]]

    if len(values[0]) != len(variables):
        raise Exceptions.any_user_error("Incorrect number of arguments or bug in my interpreter", values, variables)
    else:
        for i in range(0, len(variables)):
            v = (Calc.calculate(variables[i], scope),)
            vals = (eval(values[0][i]) if globals.is_num(values[0][i]) != 'Error' else values[0][i])
            Vars.set_val(v, vals)
    return True

def handle_output(line, scope):
    line = line.decode('string_escape')
    sep = re.findall(r'(?s)printf\s*\(\s*\"(.*)\"\s*(,.+)*\s*\)', line)
    if len(sep) == 0:
        return False
    if type(sep[0]) is str:
        sep = [[sep[0]]]
    format_string = sep[0][0]
    if sep[0][1] == '':
        globals.out.write(format_string)
    else:
        format_vars = globals.toplevelsplit(sep[0][1][1:], ',')
        for i in range(0, len(format_vars)):
            if format_vars[i] != '':
                format_vars[i] = Calc.calculate(format_vars[i].strip(), scope, globals.var_table)
        format_string = re.sub(r'%(\d*\.?\d*)(lld|ld|d)', r'%\1d', format_string)
        format_string = re.sub(r'%(\d*\.?\d*)(Lf|lf|f)', r'%\1f', format_string)
        format_string = format_string % tuple(format_vars)
        globals.out.write(format_string)
    return True
