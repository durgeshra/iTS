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
def add(arr, memarr, token, ctr, scope, cast=None):
    from .Vars import get_classes
    if token == '||' or token == '&&':
        arr.append(Types.Operator(token,ctr,cast))
        memarr.append(None)
    elif token in Globals.ops + ('&0', '|1'):
        arr.append(Types.Operator(token,ctr,cast))
        memarr.append(None)
    else:
        val, memval = get_classes(token, scope)
        arr.append(val)
        memarr.append(memval)

# Convert separated token list to postfix token list.
# Example: ['4', '/', 'y'] to  [('4', 'number'), ('y', 'int'), ('/',)]
def to_postfix(tokens, scope):
    stack, postfix, ctr, i = [], [], 0, 0
    memstack, mempf = [], []

    while i < len(tokens):
        tk = tokens[i]
        if tk in Globals.ops:
            if tk == '(':
                add(stack, memstack, tk, ctr, scope)
            elif tk == ')':
                tmptypes = []
                if stack[-1].val == '#type#':
                    while stack[-1].val != '(':
                        tmptypes.append(stack.pop())
                    stack.pop()
                    tmptypes.reverse()
                    add(stack, memstack, '#type#', ctr, scope, " ".join(k.cast for k in tmptypes))
                else:
                    while stack[-1].val != '(':
                        #add(postfix, stack.pop(), ctr, scope)
                        postfix.append(stack.pop())
                        mempf.append(memstack.pop())
                    stack.pop()
            elif len(stack) == 0 or stack[-1].val == '(':
                add(stack, memstack, tk, ctr, scope)
            else:
                if Globals.priority[tk] < Globals.priority[stack[-1].val]:
                    #add(postfix, stack.pop(), ctr, scope)
                    postfix.append(stack.pop())
                    mempf.append(memstack.pop())
                    continue

                if Globals.priority[tk] > Globals.priority[stack[-1].val]:
                    add(stack, memstack, tk, ctr, scope)

                elif Globals.priority[tk] == Globals.priority[stack[-1].val]:
                    if Globals.priority[tk] % 2 == 0:
                        #add(postfix, stack.pop(), ctr, scope)
                        postfix.append(stack.pop())
                        mempf.append(memstack.pop())
                        add(stack, memstack, tk, ctr, scope)
                    else:
                        add(stack, memstack, tk, ctr, scope)

            if tk == '&&' or tk == '||':
                add(postfix, mempf, tk, ctr, scope)
                ctr += 1

        else:
            tag = 0
            for types in Globals.data_types:
                if tk.startswith(types):
                    add(stack, memstack, '#type#', ctr, scope, tk)
                    tag = 1
                    break
            if tag == 0:
                add(postfix, mempf, tk, ctr, scope)
        i += 1
    while len(stack) > 0:
        #add(postfix, stack.pop(), ctr, scope)
        postfix.append(stack.pop())
        mempf.append(memstack.pop())
    print("Returning", postfix)
    return postfix, mempf

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
    from .Vars import get_val, set_val, get_classes
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

    postfix, mempf = to_postfix(separated_tokens, scope)
    # Convert to postfix

    #var_stack and mem_stack are always parallel to each pother, ith entry of var_stack has memory location at ith entry of mem_stack
    mem_stack, var_stack = [], []
    l = lambda: len(var_stack) - 1
    idx = 0
    for i, token in enumerate(postfix):
        if idx and postfix[i-1].val != idx:
            continue
        idx = 0
        if token.val not in Globals.ops + ('&0', '|1'):
            var_stack.append(token)
            mem_stack.append(mempf[i])
        else:
            if token.val == '---':
                val = var_stack[l()].val - 1
                set_val(mem_stack[l()], val, scope)
                var_stack[l()].setval(val)
            elif token.val == '+++':
                val = var_stack[l()].val + 1
                set_val(mem_stack[l()], val, scope)
                var_stack[l()].setval(val)
            elif token.val == '`*`':
                key = (var_stack[l()].val,)
                if key in Globals.memory:
                    var_stack[l()] = Types.construct(val = Globals.memory[key][0].v, cast = Globals.memory[key][0].type[0])
                    mem_stack[l()] = None
                else:
                    raise Exceptions.any_user_error("Invalid Memory location", key)
                # var_stack[l()] = ((get_val(var_stack[l()], scope), ), get_type(var_stack[l()], scope)) # Do not remove the comma. It forces formation of a tuple
            elif token.val == '`&`':
                val = mem_stack[l()][2]
                var_stack[l()] = Types.Pointer_T(parent_type = var_stack[l()].STR, val = val)
                mem_stack[l()] = None
            elif token.val == '`+`':
                var_stack[l()] = Types.Num_T(val = var_stack[l()].val)
                mem_stack[l()] = None
            elif token.val == '`-`':
                var_stack[l()] = Types.Num_T(val = -var_stack[l()].val)
                mem_stack[l()] = None
            elif token.val == '<<=':
                val = var_stack[l() - 1] << var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '>>=':
                val = var_stack[l() - 1] >> var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '|1':
                if var_stack[l()].val:
                    var_stack[l()] = Int_T(val = 1)
                    idx = ('||', token.ctr)
            elif token.val == '&0':
                if not var_stack[l()].val:
                    var_stack[l()] = Int_T(val = 0)
                    idx = ('&&', token.ctr)
            elif token.val == '*=':
                val = var_stack[l() - 1] * var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '|=':
                val = var_stack[l() - 1] | var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '>=':
                isGEq = var_stack[l() - 1].val >= var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val=isGEq)
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '>>':
                val = var_stack[l() - 1] >> var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '==':
                isEqual = var_stack[l() - 1].val == var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val=isEqual)
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val== '<<':
                val = var_stack[l() - 1] << var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '<=':
                isLEq = var_stack[l() - 1].val <= var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val = isLEq)
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '&=':
                val = var_stack[l() - 1] & var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '!=':
                isUnequal = var_stack[l() - 1].val != var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val = isUnequal)
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '&&':
                aAndB = var_stack[l()-1].val and var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val = aAndB)
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '||':
                aOrB = var_stack[l()-1].val or var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val = aOrB)
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '^=':
                val = var_stack[l() - 1] ^ var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '++':
                #post increment does not require value change in operation, but value in var_table is changed
                set_val(mem_stack[l()], var_stack[l()].val+1, scope)
            elif token.val == '--':
                #post decrement does not require value change in operation, but value in var_table is changed
                set_val(mem_stack[l()], var_stack[l()].val-1, scope)
            elif token.val == '/=':
                val = var_stack[l()-1] / var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '%=':
                val = var_stack[l()-1] % var_stack[l()]
                set_val(mem_stack[l()-1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '-=':
                val = var_stack[l() - 1] - var_stack[l()]
                set_val(mem_stack[l() - 1], val, scope)
                var_stack[l() - 1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '+=':
                val = var_stack[l()-1] + var_stack[l()]
                set_val(mem_stack[l()-1], val, scope)
                var_stack[l()-1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == ',':
                var_stack[l() - 1] = var_stack[l()]
                mem_stack[l()-1] = mem_stack[l()]
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '>':
                isMore = var_stack[l() - 1].val > var_stack[l()].val
                var_stack[l() - 1] = Types.Num_T(val=isMore)
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '|':
                var_stack[l() - 1] = var_stack[l() - 1] | var_stack[l()]
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '^':
                var_stack[l() - 1] = var_stack[l() - 1] ^ var_stack[l()]
                mem_stack[l() - 1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '!':
                isZero = not var_stack[l()].val
                var_stack[l()] = Types.Num_T(val = isZero)
                mem_stack[l()] = None
            elif token.val == '%':
                if var_stack[l()].val == 0:
                    raise ValueError("Modulo by 0 not allowed!")
                var_stack[l()-1] = var_stack[l()-1] % var_stack[l()]
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '&':
                var_stack[l()-1] = var_stack[l()-1] & var_stack[l()]
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '+':
                val = var_stack[l()-1] + var_stack[l()]
                var_stack[l()-1] = val
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '*':
                val = var_stack[l()-1] * var_stack[l()]
                var_stack[l() - 1] = val
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '-':
                val = var_stack[l()-1] - var_stack[l()]
                var_stack[l() - 1] = val
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '/':
                if (var_stack[l()].val == 0):
                    raise ValueError("Division by 0 not allowed!")
                val = var_stack[l()-1] / var_stack[l()]
                var_stack[l() - 1] = val
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '=':
                val = var_stack[l()].val
                set_val(mem_stack[l()-1], val, scope)
                var_stack[l()-1].setval(val)
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '<':
                isLess = var_stack[l()-1].val < var_stack[l()].val
                var_stack[l()-1] = Types.Int_Num_TT(val=isLess)
                mem_stack[l()-1] = None
                var_stack.pop()
                mem_stack.pop()
            elif token.val == '~':
                var_stack[l()] = ~var_stack[l()]
                mem_stack[l()] = None
            elif token.val == ':':
                assert postfix[i+1].val == '?'
            elif token.val == '?':
                assert postfix[i-1].val == ':'
                if var_stack[l()-2].val:
                    var_stack[l()-2] = var_stack[l()-1]
                    mem_stack[l()-2] = mem_stack[l()-1]
                else:
                    var_stack[l()-2] = var_stack[l()]
                    mem_stack[l()-2] = mem_stack[l()]
                var_stack.pop() # pop twice
                var_stack.pop()
                mem_stack.pop()
                mem_stack.pop()

            elif token.val == "#type#":
                new_type = token.cast
                if new_type == 'longlong':
                    new_type = 'long long'
                elif new_type == 'longint':
                    new_type = 'long int'
                elif new_type == 'longlongint':
                    new_type = 'long long int'
                elif new_type == 'longdouble':
                    new_type = 'long double'
                var_stack[l()] = Types.construct(val = var_stack[l()].val, cast = new_type)
                mem_stack[l()] = None
        temp = var_stack[l()]
        type_check = None
        try:
            type_check = temp.STR
        except:
            pass
        if type_check!=None:
            m1 = Globals.type_range[type_check][0]
            m2 = Globals.type_range[type_check][1]
            if type(temp.val) is int:
                temp = temp.val
            else:
                temp = 0
            if not (temp == '' or temp is None or (m1 <= temp and temp <= m2)):
                raise Exceptions.any_user_error("Value", temp, "out of bounds of the type", type_check, "which can store values from", m1, "to", m2,".")
    ret = var_stack.pop()
    if var_stack:
        raise Exceptions.any_user_error("I don't think the expression in current line makes any sense.")
    if isinstance(ret, Types.String):
        return get_val(ret.val, scope)
    else:
        return ret.val

calculate = Globals.analyze(calculate)
