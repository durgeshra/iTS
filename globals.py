global var_table
global inp
inp = ''
var_table = {}


priority = {
    '->': 100, '++': 100, '--': 100,
    '+++': 91, '---': 91, '#': 91, '_': 91, '!': 91, '~': 91, '#type#': 91,
    '*': 80, '/': 80, '%': 80,
    '+': 78, '-': 78,
    '>>': 76, '<<': 76,
    '<=': 70, '>=': 70, '>': 70, '<': 70,
    '==': 66, '!=': 66,
    '&': 58, '^': 56, '|': 54, '&&': 52, '||': 50,
    '? :': 45,
    '=': 41, '+=': 41, '-=': 41, '*=': 41, '/=': 41,
    '%=': 41, '&=': 41, '^=': 41, '|=': 41,
    '>>=': 41, '<<=': 41,
    ',': 10
}


ops = (
    '#type#', '---', '? :', '+++', '<<=', '>>=', '*=', '|=', '>=', '>>', '==', '<<',
    '<=', '&=', '!=', '&&', '||', '^=', '++', '--', '/=', '%=', '-=', '->',
    '+=', ',', '>', '|', '^', '!', '%', '&', '+', '#', '_', '*', '-', '/', '=',
    '<', '~', '(', ')'
)


def in_var_table(var, scope):
    if type(scope) is str:
        scope = scope.split(' ')
    else:
        scope = scope[:]
    while len(scope) > 0:
        if (var, " ".join(scope)) in var_table:
            return var, " ".join(scope)
        scope.pop()
    return 0