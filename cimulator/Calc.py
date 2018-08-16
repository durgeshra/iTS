from __future__ import print_function, absolute_import
import re

from .Functions import pass_to_func
from .Globals import is_num, print1, print2, print3
from . import Globals
from . import Exceptions
from . import FakeMath
from . import Types

# Differentate between postfix and prefix increment operators.
def pre_post_handle(tokens):
    for i, tk in enumerate(tokens):
        if tk == '--':
            if i < len(tokens)-1 and tokens[i+1] not in Globals.ops:
                tokens[i] = '---'
        if tk == '++':
            if i < len(tokens)-1 and tokens[i+1] not in Globals.ops:
                tokens[i] = '+++'
    return tokens

pre_post_handle = Globals.analyze(pre_post_handle)

# Separate out the tokens from an expression. i.e something like
# '5 + 4' would become ['5', '+', '4']
def sep(expr):
    print1(expr)
    i, token, sep_tokens = 0, [], []

    while i < len(expr) and expr[i] != ';' :

        while i < len(expr) and expr[i] == ' ' :
            if token:
                sep_tokens.append(''.join(token))
                token = []
            i += 1

        checkOps = Globals.startDict

        if expr[i] in checkOps:
            for ex in checkOps[expr[i]]:
                if expr.startswith(ex, i):
                    if ex != '(' and ex != '[':
                        if token != []:
                            sep_tokens.append(''.join(token))
                        token = []
                    if ex == '(':
                        if token == []:
                            sep_tokens.append(ex)
                        else:
                            j = i + 1
                            expression = ['(']
                            bracks = 1
                            while bracks > 0:
                                expression.append(expr[j])
                                if expr[j] == '(':
                                    bracks += 1
                                if expr[j] == ')':
                                    bracks -= 1
                                j += 1
                            i += len(expression) - 1
                            token += expression
                    elif ex == '[':
                        j = i + 1
                        expression = ['[']
                        bracks = 1
                        while bracks > 0:
                            expression += expr[j]
                            if expr[j] == '[' and expr[j-1]!="'":
                                bracks += 1;
                            if expr[j] == ']' and expr[j-1]!="'":
                                bracks -= 1;
                            j += 1
                        i += len(expression) - 1
                        token += expression
                    elif ex == '\'':
                        assert token == []
                        j = i + 1
                        expression = ['\'']
                        while expr[j] != "'" or expr[j-1] == '\\':
                            expression += expr[j]
                            j += 1
                        expression += expr[j]
                        i += len(expression) - 1
                        token += expression
                    elif ex == '\"':
                        assert token == []
                        j = i + 1
                        expression = ['\"']
                        while expr[j] != '\"' or expr[j-1] == '\\':
                            expression += expr[j]
                            j += 1
                        expression += expr[j]
                        i += len(expression) - 1
                        token += expression
                    else:
                        sep_tokens.append(ex)
                    i += len(ex) - 1
                    break
        else:
            token.append(expr[i])
        i += 1
    if token != []:
        sep_tokens.append(''.join(token))

    print1("Returning", sep_tokens)
    return sep_tokens

sep = Globals.analyze(sep)


# Convert operators like '+' which have overloaded binary and unary
# functions into differentiated unary counterparts, '`+`' for example.
def unary_handle(separated_tokens):
    flag = 1
    for i, token in enumerate(separated_tokens):

        if token in Globals.unary_ops and flag:
            separated_tokens[i] = Globals.unary_ops[token]
            continue

        if token in Globals.bin_ops or token == '(':
            flag = 1
            continue
        flag = 0

    return separated_tokens

unary_handle = Globals.analyze(unary_handle)


# Add token to stack, taking extra care of && and || shortcircuiting
# operators. (Using &0 , counter substitution). Also appends type
# information wherever known.
def add(arr, token, ctr, scope):
    from .Vars import get_val, set_val, get_type

    if type(token) is tuple:
        arr.append(token)
    else:
        if token == '||' or token == '&&':
            #arr.append((token, ctr))
            a = Types.AndOr(token,ctr)
            arr.append(a)
        elif token in Globals.ops + ('&0', '|1'):
            #arr.append((token,))
            a = Types.Operator(token)
            arr.append(a)
        else:
            got_type = get_type(token, scope)
            #arr.append((token, got_type))
            if got_type=="number":
                a = Types.Stranger(token)
                arr.append(a)

            #not handled funcs yet
            else:
                if got_type=="char":
                    arr.append(Types.Char_T(varname=token))
                elif got_type=="int":
                    arr.append(Types.Int_T(varname=token))
                elif got_type=="long" or got_type=="long int":
                    arr.append(Types.Long_T(varname=token))
                elif got_type=="long long" or got_type=="long long int":
                    arr.append(Types.LongLong_T(varname=token))
                elif got_type=="pointer":
                    arr.append(Types.Pointer_T(varname=token))
                elif got_type=="float":
                    arr.append(Types.Float_T(varname=token))
                elif got_type=="double":
                    arr.append(Types.Double_T(varname=token))
                elif got_type=="long double":
                    arr.append(Types.LongDouble_T(varname=token))
                elif got_type=="function":
                    arr.append(Types.Function(details=token))

# Convert separated token list to postfix token list.
# Example: ['4', '/', 'y'] to  [('4', 'number'), ('y', 'int'), ('/',)]
def to_postfix(tokens, scope):
    stack, postfix, ctr, i = [], [], 0, 0

    while i < len(tokens):
        tk = tokens[i]
        if tk in Globals.ops:
            if tk == '(':
                add(stack, tk, ctr, scope)

            elif tk == ')':
                tmptypes = []
                if stack[-1][0] == '#type#':
                    while stack[-1][0] != '(':
                        tmptypes.append(stack.pop())
                    stack.pop()
                    tmptypes.reverse()
                    add(stack, ('#type#', " ".join(k[1] for k in tmptypes)), ctr, scope)
                else:
                    while stack[-1][0] != '(':
                        postfix.append(stack.pop())
                    stack.pop()
            elif len(stack) == 0 or stack[-1].__repr__() == '(':
                add(stack, tk, ctr, scope)

            else:
                if Globals.priority[tk] < Globals.priority[stack[-1].__repr__()]:
                    postfix.append(stack.pop())
                    continue

                if Globals.priority[tk] > Globals.priority[stack[-1].__repr__()]:
                    add(stack, tk, ctr, scope)

                elif Globals.priority[tk] == Globals.priority[stack[-1].__repr__()]:
                    if Globals.priority[tk] % 2 == 0:
                        postfix.append(stack.pop())
                        add(stack, tk, ctr, scope)
                    else:
                        add(stack, tk, ctr, scope)

        else:
            tag = 0
            for types in Globals.data_types:
                if tk.startswith(types):
                    add(stack, ('#type#', tk), ctr, scope)
                    tag = 1
                    break
            if tag == 0:
                add(postfix, tk, ctr, scope)
        i += 1
    while len(stack) > 0:
        postfix.append(stack.pop())

    print("Returning", postfix)
    return postfix

to_postfix = Globals.analyze(to_postfix)

# Return the type with highest priority in coersion.
# Eg. Lf>lf>f>lld>ld>d etc.
def max_type(t1, t2='number', t3='number'):

    p_t = Globals.priority_type

    if(p_t[t1] >= p_t[t2] and p_t[t1] >= p_t[t3]):
        return t1

    elif(p_t[t2] >= p_t[t1] and p_t[t2] >= p_t[t3]):
        return t2

    elif(p_t[t3] >= p_t[t1] and p_t[t3] >= p_t[t2]):
        return t3


# Debugging only function. Slows down code considerably.
def caller_name():
    import inspect
    frame=inspect.currentframe()
    frame=frame.f_back.f_back
    code=frame.f_code
    return code.co_filename




# Backbone function of the whole project. Evaluates any
# expression, assigns variables, looks up memory addresses,
# everything. Can get input like '5+(a=4)+(a==4)?1:2'.

def calculate(expr, scope, vartable=Globals.var_table):
    from .Vars import get_val, set_val, get_type, handle_address
    from . import Runtime

    if re.match(r'^(?s)\s*$', expr):
        return 0
    # If string has nothing, return 0. *TODO: Fix this "tape"

    if re.match(r'^(?s)\s*{\s*', expr):
        return expr
    # Not sure what this did. *TODO: Ask Kapila

    separated_tokens = sep(expr.strip())
    # Separate out all tokens

    separated_tokens = unary_handle(separated_tokens)
    # Fix unary operators like +, - etc.

    separated_tokens = pre_post_handle(separated_tokens)
    # Replace pre increment ++ and --
    postfix = to_postfix(separated_tokens, scope)
    # Convert to postfix

    stack, var_stack = [], []
    l = lambda: len(var_stack) - 1
    idx = 0
    for i, tk in enumerate(postfix):
        token = tk.__repr__()
        if idx and postfix[i-1] != idx:
            continue
        idx = 0
        if token not in Globals.ops + ('&0', '|1'):
            var_stack.append(tk)
        else:
            #APPARENTLY NOT USED ANYMORE, NEED TO CONFIRM BEFORE DELETING

            # if token in Globals.bin_ops:
            #     var_stack[l()] = var_stack[l()].__repr__()
            #     var_stack[l()-1] = var_stack[l()-1].__repr__()
            # elif token in Globals.un_ops + ('&0', '|1'):
            #     var_stack[l()] = var_stack[l()].__repr__()
            # elif token == '?':
            #     var_stack[l()] = var_stack[l()].__repr__()
            #     var_stack[l()-1] = var_stack[l()-1].__repr__()
            #     var_stack[l()-2] = var_stack[l()-2].__repr__()

            ############################################################
            if token == '---':
                key = Runtime.get_key(var_stack[l()], scope)
                val = get_val(key, scope) - 1
                set_val(key, val, scope)
                var_stack[l()].setval(val)
            elif token == '+++':
                key = Runtime.get_key(var_stack[l()], scope)
                val = get_val(key, scope) + 1
                set_val(key, val, scope)
                var_stack[l()].setval(val)
            elif token == '`*`':
                val = handle_address(get_val(var_stack[l()], scope), isinstance(var_stack[l()],Types.Pointer_T))
                var_stack[l()] = Types.Num_T(val)
            elif token == '`&`':
                key = Runtime.get_key(var_stack[l()], scope)
                if type(key) is not tuple:
                    raise Exceptions.any_user_error("Something Wrong in the interpreter. Bug report filed.")
                elif len(key) == 1:
                    mem = key[0]
                else:
                    mem = vartable[key][3]
                var_stack[l()] = Types.Pointer_T(mem)
            elif token == '`+`':
                var_stack[l()].setval(var_stack[l()])
            elif token == '`-`':
                var_stack[l()].setval(-get_val(var_stack[l()], scope))
            elif token == '<<=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                set_val(key, get_val(key, scope) << get_val(var_stack[l()], scope), scope)
                var_stack[l()-1] = var_stack[l()-1] << var_stack[l()]
                var_stack.pop()
            elif token == '>>=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                set_val(key, get_val(key, scope) >> get_val(var_stack[l()], scope), scope)
                var_stack[l()-1] = var_stack[l()-1] >> var_stack[l()]
                var_stack.pop()
            elif token == '|1':
                if get_val(var_stack[l()], scope):
                    var_stack[l()] = Types.Int_T(val=1)
                    idx = ('||', tk.datatype())
                    ###########short circuiting##############
                else:
                    var_stack[l()].setval(get_val(var_stack[l()], scope))
            elif token == '&0':
                if not get_val(var_stack[l()], scope):
                    var_stack[l()] = Types.Num_T(0)
                    idx = ('&&', tk.datatype())
                else:
                    var_stack[l()].setval(get_val(var_stack[l()], scope))
            elif token == '*=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(key, scope) * get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l() - 1] = var_stack[l()-1] * var_stack[l()]
                var_stack.pop()
            elif token == '|=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(key, scope) | get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l() - 1] = var_stack[l()-1] | var_stack[l()]
                var_stack.pop()
            elif token == '>=':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) >= get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '>>':
                var_stack[l() - 1] = var_stack[l() - 1] >> var_stack[l()]
                var_stack.pop()
            elif token == '==':
                var_stack[l() - 1] = (Types.Int_T(val=1) if (get_val(var_stack[l() - 1], scope) == get_val(var_stack[l()], scope)) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '<<':
                var_stack[l() - 1] = var_stack[l() - 1] << var_stack[l()]
            elif token == '<=':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) <= get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '&=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(key, scope) & get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l() - 1] = var_stack[l()-1] & var_stack[l()]
                var_stack.pop()
            elif token == '!=':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) != get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '&&':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) and get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '||':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) or get_val(var_stack[l()], scope) else Types.Num_T(0))
                var_stack.pop()
            elif token == '^=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(key, scope) ^ get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l() - 1] = var_stack[l()-1] ^ var_stack[l()]
                var_stack.pop()
            elif token == '++':
                key = Runtime.get_key(var_stack[l()], scope)
                val = get_val(key, scope) + 1
                set_val(key, val, scope)
                var_stack[l()].setval(val-1)
            elif token == '--':
                key = Runtime.get_key(var_stack[l()], scope)
                val = get_val(key, scope) - 1
                set_val(key, val, scope)
                var_stack[l()].setval(val+1)
            # elif token == '/=':
            #     key = Runtime.get_key(var_stack[l()-1], scope)
            #     if get_val(var_stack[l()], scope) is 0:
            #         raise Exceptions.any_user_error("Division by 0 not allowed!")
            #
            #     val = get_val(key, scope) / get_val(var_stack[l()], scope)
            #     max_t = max_type(t2)
            #     if max_t in "number long long int":
            #         val = int(val)
            #
            #     set_val(key, val, scope)
            #     var_stack[l() - 1] = var_stack[l()-1] / var_stack[l()]
            #     var_stack.pop()
            # elif token == '%=':
            #     if t1 in ['float', 'double', 'long double', 'longdouble'] or t2 in ['float', 'double', 'long double', 'longdouble']:
            #         raise Exceptions.any_user_error("Modulo operation not allowed with floating point numbers.")
            #     key = Runtime.get_key(var_stack[l()-1], scope)
            #     if get_val(var_stack[l()], scope) is 0:
            #         raise Exceptions.any_user_error("Modulo by 0 not allowed!")
            #     val = get_val(key, scope) % get_val(var_stack[l()], scope)
            #     set_val(key, val, scope)
            #     var_stack[l() - 1] = var_stack[l()-1] % var_stack[l()]
            #     var_stack.pop()
            # elif token == '-=':
            #     key = Runtime.get_key(var_stack[l()-1], scope)
            #     val = get_val(key, scope) - get_val(var_stack[l()], scope)
            #     set_val(key, val, scope)
            #     var_stack[l() - 1] = var_stack[l()-1] - var_stack[l()]
            #     var_stack.pop()
            elif token == '+=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(key, scope) + get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l() - 1] = var_stack[l()-1] + var_stack[l()]
                var_stack.pop()
                #UNCLEAR####################################
            # elif token == ',':
            #     var_stack[l() - 1] = Types.Num_T(var_stack[l()], max_type(t1, t2))
            #     var_stack.pop()
            elif token == '>':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) > get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '|':
                var_stack[l() - 1] = var_stack[l() - 1] | var_stack[l()]
                var_stack.pop()
            elif token == '^':
                var_stack[l() - 1] = var_stack[l() - 1] ^ var_stack[l()]
                var_stack.pop()
            elif token == '!':
                var_stack[l()] = (var_stack[l()].setval(0) if get_val(var_stack[l()], scope) else var_stack[l()].setval(1))
            elif token == '%':
                if get_val(var_stack[l()], scope) == 0:
                    raise Exceptions.any_user_error("Modulo by 0 not allowed!")
                    var_stack[l() - 1] = var_stack[l() - 1] % var_stack[l()]
                var_stack.pop()
            elif token == '&':
                var_stack[l() - 1] = var_stack[l() - 1] & var_stack[l()]
                var_stack.pop()
            elif token == '+':
                var_stack[l() - 1] = var_stack[l() - 1] + var_stack[l()]
                var_stack.pop()
            elif token == '*':
                var_stack[l() - 1] = var_stack[l() - 1] * var_stack[l()]
                var_stack.pop()
            elif token == '-':
                var_stack[l() - 1] = var_stack[l() - 1] - var_stack[l()]
                var_stack.pop()
            elif token == '/':
                if get_val(var_stack[l()], scope) == 0:
                    raise Exceptions.any_user_error("Division by 0 not allowed!")
                v1 = get_val(var_stack[l() - 1], scope)
                v2 = get_val(var_stack[l()], scope)
                var_stack[l() - 1] = var_stack[l() - 1] / var_stack[l()]
                var_stack.pop()
            elif token == '=':
                key = Runtime.get_key(var_stack[l()-1], scope)
                val = get_val(var_stack[l()], scope)
                set_val(key, val, scope)
                var_stack[l()-1].setval(val)
                var_stack.pop()
            elif token == '<':
                var_stack[l() - 1] = (Types.Int_T(val=1) if get_val(var_stack[l() - 1], scope) < get_val(var_stack[l()], scope) else Types.Int_T(val=0))
                var_stack.pop()
            elif token == '~':
                ~var_stack[l()]
            elif token == ':':
                assert postfix[i+1].__repr__ == '?'
            elif token == '?':
                assert postfix[i-1].__repr__ == ':'
                if get_val(var_stack[l()-2], scope):
                    var_stack[l()-2] = var_stack[l()-1]
                else:
                    var_stack[l()-2] = var_stack[l()]
                var_stack.pop() # pop twice
                var_stack.pop()

            elif token == "#type#":
                new_type = tk.datatype()
                if new_type == 'longlong':
                    new_type = 'long long'
                elif new_type == 'longint':
                    new_type = 'long int'
                elif new_type == 'longlongint':
                    new_type = 'long long int'
                elif new_type == 'longdouble':
                    new_type = 'long double'
                if new_type in ['float', 'double', 'long double']:
                    if type(var_stack[l()]) is 'str':
                        raise Exceptions.any_user_error("User trying to convert", get_val(var_stack[l()], scope),"to float.")
                    else:
                        var_stack[l()] =  Types.Num_T(float(get_val(var_stack[l()], scope)), new_type)
                elif new_type in ['int', 'long', 'long int', 'long long int', 'long long']:
                    if type(var_stack[l()]) is 'char':
                        var_stack[l()] =  Types.Num_T(ord(get_val(var_stack[l()], scope)), new_type)
                    else:
                        var_stack[l()] = Types.Num_T(int(get_val(var_stack[l()], scope)), new_type)
                elif new_type is 'char':
                    if type(var_stack[l()]) in ['float', 'double', 'long double']:
                        raise Exceptions.any_user_error("User trying to convert", get_val(var_stack[l()], scope) ,"to string.")
                    else:
                        var_stack[l()] = Types.Num_T(chr(get_val(var_stack[l()], scope)), new_type)
        temp = var_stack[l()]
        #if temp.datatype() not in ['number', 'void']:
            #type_check = temp.datatype()
            #m1 = Globals.type_range[temp[1]][0]
            #m2 = Globals.type_range[temp[1]][1]
            #if type(temp[0]) is int:
            #    temp = temp[0]
            #else:
            #    temp = 0
            #if not (temp == '' or temp is None or (m1 <= temp and temp <= m2)):
            #    raise Exceptions.any_user_error("Value", temp, "out of bounds of the type", type_check, "which can store values from", m1, "to", m2,".")
    ret = var_stack.pop()
    if var_stack:
        raise Exceptions.any_user_error("I don't think the expression in current line makes any sense.")
    r = get_val(ret, scope)
    try:
        Globals.calc_type = ret.datatype()
    except:
        pass
    return r

calculate = Globals.analyze(calculate)
