from __future__ import print_function, absolute_import
import re

from . import Globals
from . import Exceptions
from . import Types

def invoke(name, params, scope):
    if name == 'sizeof':
        if len(params) != 1:
            raise Exceptions.any_user_error("Incorrect number of parameters.")
        t = re.findall(r'\*', params[0])
        if t:
            return Types.Int_T(val=Globals.size_of['pointer'])
        else:
            return Types.Int_T(Globals.size_of[params[0].strip()])
    if name == 'malloc':
        raise Exceptions.any_user_error("Malloc hasn't been implemented yet.")
