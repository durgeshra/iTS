from __future__ import print_function, absolute_import, division
from abc import abstractmethod

from .Exceptions import any_user_error
from .Globals import priority_type
from . import Globals

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

    # Implementation of the following functions is common for all
    @coerce
    def __add__(self, other):
        val = self.val + other.val
        return self.__class__(val=val)

    @coerce
    def __sub__(self, other):
        val = self.val - other.val
        return self.__class__(val=val)

    @coerce
    def __mul__(self, other):
        val = self.val * other.val
        return self.__class__(val=val)

    @coerce
    def __pow__(self, other, modulo=float('Inf')):
        val = self.val ** other.val
        return self.__class__(val=val)

    def __neg__(self):
        return self.__class__(val=-self.val)

    def __pos__(self):
        return self.__class__(val=self.val)

    def __abs__(self):
        return self.__class__(val=abs(self.val))

    def __invert__(self):
        return self.__class__(val=~self.val)

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

class Point_T(Numeric):
    typeclass = "point"
    val = 0.0

    def __init__(self, val=None, var=None, cast=None, level=None, tags=None):
        if val!=None:
            try:
                val = float(val)
            except:
                ValueError(val+" cannot be instantiated to float type.")
        self.val = val
        self.var = var
        self.cast = cast
        self.level = level
        self.tags = tags

    @coerce
    def __div__(self, other):
        if other.val == 0:
            raise any_user_error("Division by 0 not allowed!")
        val = self.val / other.val
        return self.__class__(val=val)

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

    def setval(self, val):
        self.val = float(val)

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

    def __init__(self, val=None, var=None, cast=None, level=None, tags=None):
        if val!=None:
            try:
                val = ord(val)
            except:
                val = int(val)
        if val!=None and (val > self.MAX or val < self.MIN):
            raise any_user_error(
                    "Value", val, "out of bounds of the type",
                    self.STR, "which can store values from",
                    self.MIN, "to", self.MAX,".")
        self.val = val
        self.var = var
        self.cast = cast
        self.level = level
        self.tags = tags

    @coerce
    def __div__(self, other):
        if other.val == 0:
            raise ValueError("Division by 0 not allowed!")
        val = self.val / other.val
        return self.__class__(val=val)

    @coerce
    def __divmod__(self, other):
        if other.val == 0:
            raise ValueError("Division by 0 not allowed!")
        if isinstance(self, Num_T) and isinstance(other, Num_T):
            val = self.val // other.val
            mod = self.val % other.val
            return (self.__class__(val=val), self.__class__(val=mod))
        else:
            raise TypeError("Cannot apply modulus operation on " + self.STR + " and " + other.STR + " types.")

    @coerce
    def __mod__(self, other):
        if other.val == 0:
            raise ValueError("Modulo by 0 not allowed!")
        if isinstance(self, Num_T) and isinstance(other, Num_T):
            val = self.val % other.val
            return self.__class__(val=val)
        else:
            raise TypeError("Cannot apply modulus operation on " + self.STR + " and " + other.STR + " types.")

    @coerce
    def __lshift__(self, other):
        val = self.val << other.val
        return self.__class__(val=val)

    @coerce
    def __rshift__(self, other):
        val = self.val >> other.val
        return self.__class__(val=val)

    @coerce
    def __and__(self, other):
        val = self.val & other.val
        return self.__class__(val=val)

    @coerce
    def __xor__(self, other):
        val = self.val ^ other.val
        return self.__class__(val=val)

    @coerce
    def __or__(self, other):
        val = self.val | other.val
        return self.__class__(val=val)

    def setval(self, val):
        try:
            val = ord(val)
        except:
            val = int(val)
        if (val > self.MAX or val < self.MIN):
            raise any_user_error(
                    "Value", val, "out of bounds of the type",
                    self.STR, "which can store values from",
                    self.MIN, "to", self.MAX,".")
        self.val = val


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

    def __init__(self, parent_type, val=None, var=None, cast=None, level=None, tags=None):
        Num_T.__init__(self, val, var, cast, level, tags)
        self.parent_type = parent_type

class Operator:
    STR = "operator"

    def __init__(self, val, ctr=0, cast=None):
        self.val = val
        self.ctr = ctr
        self.cast = cast

    def __repr__(self):
        return str(self.val)

class String:

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return str(self.val)

def construct(val, cast, var=None, level=None, tags=None, parent_type=None):
    if cast=="char":
        return Char_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast=="int":
        return Int_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "long" or cast == "long int":
        return Long_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "long long" or cast == "long long int":
        return LongLong_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "float":
        return Float_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "double":
        return Double_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "long double":
        return LongDouble_T(val=val, var=var, cast=cast, level=level, tags=tags)
    elif cast == "pointer":
        return Pointer_T(val=val, var=var, cast=cast, level=level, tags=tags, parent_type=parent_type)



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
