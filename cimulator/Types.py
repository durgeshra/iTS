from __future__ import print_function, absolute_import, division
from abc import abstractmethod

from .Exceptions import any_user_error
from .Globals import priority_type
from . import Globals
import re

def typecast(obj, type_T, force=False):
    if obj.typeclass == 'point' and type_T.typeclass == 'num':
        if not force:
            raise any_user_error(
                    "Value", obj.val, "implicitly converted to",
                    int(obj.val), "causing possible loss of precision. ",
                    "Please use explicit type casting to allow this.")
    return type_T(obj.val)

def common_type(obj1, obj2):
    p1 = priority_type[obj1.STR]
    p2 = priority_type[obj2.STR]

    if p1 > p2:
        obj2 = typecast(obj2, type(obj1))
    else:
        obj1 = typecast(obj1, type(obj2))

    return (obj1, obj2)

def coerce(fnx):
    def output(obj1, obj2):
        if type(obj1) == type(obj2):
            return fnx(obj1, obj2)
        obj1, obj2 = common_type(obj1, obj2)
        return getattr(obj1, fnx.__name__)(obj2)
    return output

class Numeric:
    MAX =  float('Inf')
    MIN = -float('Inf')
    val = 0.0

    @abstractmethod
    def __div__(self, other):
        pass

    @abstractmethod
    def __divmod__(self, other):
        pass

    @abstractmethod
    def __mod__(self, other):
        pass

    @abstractmethod
    def __lshift__(self, other):
        pass

    @abstractmethod
    def __rshift__(self, other):
        pass

    @abstractmethod
    def __and__(self, other):
        pass

    @abstractmethod
    def __xor__(self, other):
        pass

    @abstractmethod
    def __or__(self, other):
        pass

    # Implementation of the following functions is common for all types.
    @coerce
    def __add__(self, other):
        val = self.val + other.val
        return type(self)(val)

    @coerce
    def __sub__(self, other):
        val = self.val - other.val
        return type(self)(val)

    @coerce
    def __mul__(self, other):
        val = self.val * other.val
        return type(self)(val)

    @coerce
    def __pow__(self, other, modulo=float('Inf')):
        val = self.val ** other.val
        return type(self)(val)

    def __neg__(self):
        return type(self)(-self.val)

    def __pos__(self):
        return type(self)(self.val)

    def __abs__(self):
        return type(self)(abs(self.val))

    def __invert__(self):
        return type(self)(~self.val)

    def __int__(self):
        return int(self.val)

    def __long__(self):
        return long(self.val)

    def __float__(self):
        return float(self.val)

    def __oct__(self):
        return oct(self.val)

    def __hex__(self):
        return hex(self.val)

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self.val)

    def myname(self):
        return self.varname

    def setval(self,value):
        self.val = value

class Point_T(Numeric):
    typeclass = "point"
    val = 0.0

    def __init__(self, val=None, varname=None):
        val = float(val)
        self.val = val
        self.varname = None

    @coerce
    def __div__(self, other):
        if other.val == 0:
            raise any_user_error("Division by 0 not allowed!")
        val = self.val / other.val
        return type(self)(val)

    @coerce
    def __divmod__(self, other):
        if other.val == 0:
            raise any_user_error("Division by 0 not allowed!")
        raise any_user_error("Modulo applied on types", self.STR, "and",
                other.STR, "which is not allowed. Use modulo on integer ",
                "(and related) types only.")

    @coerce
    def __mod__(self, other):
        raise any_user_error("Modulo applied on types", self.STR, "and",
                other.STR, "which is not allowed. Use modulo on integer ",
                "(and related) types only.")

    @coerce
    def __lshift__(self, other):
        raise any_user_error("Left shift (<<) applied on types", self.STR,
                "and", other.STR, "which is not allowed. Use it on ",
                "integer (and related) types only.")

    @coerce
    def __rshift__(self, other):
        raise any_user_error("Right shift (>>) applied on types", self.STR,
                "and", other.STR, "which is not allowed. Use it on ",
                "integer (and related) types only.")

    @coerce
    def __and__(self, other):
        raise any_user_error("Bitwise and (&) applied on types", self.STR,
                "and", other.STR, "which is not allowed. Use it on ",
                "integer (and related) types only.")

    @coerce
    def __xor__(self, other):
        raise any_user_error("Bitwise XOR (^) applied on types", self.STR,
                "and", other.STR, "which is not allowed. Use it on ",
                "integer (and related) types only.")

    @coerce
    def __or__(self, other):
        raise any_user_error("Bitwise OR ( | ) applied on types", self.STR,
                "and", other.STR, "which is not allowed. Use it on ",
                "integer (and related) types only.")

class Float_T(Point_T):
    STR = 'float'

class Double_T(Point_T):
    STR = 'double'

class LongDouble_T(Point_T):
    STR = 'long double'

class Num_T(Numeric):
    STR = "number"
    MAX =  2**127 - 1
    MIN = -2**127
    typeclass = "num"

    val = 0

    def __init__(self, val=None, varname=None):
        #val = int(val)
        # if val > self.MAX or val < self.MIN:
        #     raise any_user_error(
        #             "Value", val, "out of bounds of the type",
        #             self.STR, "which can store values from",
        #             self.MIN, "to", self.MAX,".")
        if val==None:
            self.val = val
        else:
            self.val = int(val)
        self.varname = varname

    @coerce
    def __div__(self, other):
        if other.val == 0:
            raise any_user_error("Division by 0 not allowed!")
        val = self.val // other.val
        return type(self)(val)

    @coerce
    def __divmod__(self, other):
        if other.val == 0:
            raise any_user_error("Division by 0 not allowed!")
        val = self.val // other.val
        mod = self.val % other.val
        return (type(self)(val), type(self)(mod))

    @coerce
    def __mod__(self, other):
        if other.val == 0:
            raise any_user_error("Modulo by 0 not allowed!")
        val = self.val % other.val
        return type(self)(val)

    @coerce
    def __lshift__(self, other):
        val = self.val << other.val
        return type(self)(val)

    @coerce
    def __rshift__(self, other):
        val = self.val >> other.val
        return type(self)(val)

    @coerce
    def __and__(self, other):
        val = self.val & other.val
        return type(self)(val)

    @coerce
    def __xor__(self, other):
        val = self.val ^ other.val
        return type(self)(val)

    @coerce
    def __or__(self, other):
        val = self.val | other.val
        return type(self)(val)


class Char_T(Num_T):
    STR = "char"
    MAX =  2**7 - 1
    MIN = -2**7

class Int_T(Num_T):
    STR = "int"
    MAX =  2**31 - 1
    MIN = -2**31

class Long_T(Num_T):
    STR = "long"
    MAX =  2**63 - 1
    MIN = -2**63

class LongLong_T(Num_T):
    STR = "long long"
    MAX =  2**63 - 1
    MIN = -2**63

class Pointer_T(Num_T):
    STR = "pointer"

class AndOr():

    def __init__(self,val,count):
        self.val = val
        self.count = count

    def __repr__(self):
        return self.val

    def count(self):
        return self.count

class Stranger(Numeric):

    def __init__(self,val):
        self.val = val

    def setval(self,value):
        self.val = value

    def __repr__(self):
        return self.val

class Function():

    def __init__(self,details,ret_type=None):

        #if type in Globals.data_types:
        self.details = re.findall('^\s*([a-zA-Z_]+[a-zA-Z0-9_]*)\s*\((.*)\)\s*$', details)[0]
        self.ret_type = ret_type
        #else:
        #    raise ValueError("%s is not a data type" % type)

    def __repr__(self):
        return str(self.details)

    def return_type(self):
        return str(self.ret_type)

class Operator:

    def __init__(self,val):
        if val in Globals.ops + ('&0', '|1'):
            self.val = val
        else:
            raise ValueError("%s is not an operator" %val)

    def __repr__(self):
        return str(self.val)


type_map = {
        "number"        : Num_T,
        "char"          : Char_T,
        "int"           : Int_T,
        "long"          : Long_T,
        "long int"      : Long_T,
        "long long"     : LongLong_T,
        "long long int" : LongLong_T,

        "float"         : Float_T,
        "double"        : Double_T,
        "long double"   : LongDouble_T,
}
