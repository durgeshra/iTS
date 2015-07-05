import sys
import globals
import PreProcessing
import Runtime
import Exceptions
#import Gui

print "ARGS", sys.argv

filename = sys.argv[1]

# inp variable stores user input.
if sys.argv[3] == 'stdin':
    globals.inp = sys.stdin.read()
else:
    globals.inp = open(sys.argv[3]).read()

if sys.argv[4] == 'stderr':
    globals.out = sys.stderr
else:
    globals.out = open(sys.argv[4], 'w')

# priority variable is a dictionary of operators and their priorities.
priority = globals.priority

# ops is a list of all operators.
ops = globals.ops

# CodeFile stores a reference to the c file that has to be parsed.
CodeFile = open(filename)

# Preprocessor does some work here
code = PreProcessing.use_c_preprocessor(filename)
# print code
# code = PreProcessing.get_code(CodeFile)
code = PreProcessing.nest(code)
#Gui.make_ui(code)
# print globals.type_range
# Access is used to keep track of current scope
Access = 'global'
globals.setup()
print code
# Build a dictionary of functions and run main
try:
    Runtime.traverse(code, Access)
except Exceptions.main_executed as e:
    print e.message
