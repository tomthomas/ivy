# global
import numpy as np
from typing import Optional
import numpy.array_api as npa

try:
    from scipy.special import erf as _erf
except (ImportError, ModuleNotFoundError):
    _erf = None


def bitwise_left_shift(x1: np.ndarray,
                       x2: np.ndarray)\
                       -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.left_shift(x1, x2)


def add(x1: np.ndarray,
        x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    return np.asarray(npa.add(npa.asarray(x1), npa.asarray(x2)))


def pow(x1: np.ndarray,
        x2: np.ndarray)\
        -> np.ndarray:
    if hasattr(x1, 'dtype') and hasattr(x2, 'dtype'):
        promoted_type = np.promote_types(x1.dtype, x2.dtype)
        x1, x2 = np.asarray(x1), np.asarray(x2)
        x1 = x1.astype(promoted_type)
        x2 = x2.astype(promoted_type)
    elif not hasattr(x2, 'dtype'):
        x2 = np.array(x2, dtype=x1.dtype)
    return np.power(x1, x2)


def bitwise_xor(x1: np.ndarray,
                x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    return npa.bitwise_xor(npa.asarray(x1), npa.asarray(x2))

def exp(x: np.ndarray)\
        -> np.ndarray:
    return np.exp(x)

def expm1(x: np.ndarray)\
        -> np.ndarray:
    return np.expm1(x)


def bitwise_invert(x: np.ndarray)\
        -> np.ndarray:
    return np.invert(x)


def bitwise_and(x1: np.ndarray,
                x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.bitwise_and(x1, x2)


def equal(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return x1 == x2


def greater(x1: np.ndarray, x2: np.ndarray) \
        -> np.ndarray:
    return np.greater(x1, x2)


def greater_equal(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return np.greater_equal(x1, x2)


def less_equal(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return x1 <= x2


def multiply(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if hasattr(x1, 'dtype') and hasattr(x2, 'dtype'):
        promoted_type = np.promote_types(x1.dtype, x2.dtype)
        x1, x2 = np.asarray(x1), np.asarray(x2)
        x1 = x1.astype(promoted_type)
        x2 = x2.astype(promoted_type)
    elif not hasattr(x2, 'dtype'):
        x2 = np.array(x2, dtype=x1.dtype)
    return np.multiply(x1, x2)


def ceil(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.ceil(npa.asarray(x)))


def floor(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.floor(npa.asarray(x)))

def sign(x: np.ndarray)\
        -> np.ndarray:
    return np.sign(x)

def sqrt(x: np.ndarray)\
        -> np.ndarray:
    return np.sqrt(x)


def isfinite(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.isfinite(npa.asarray(x)))


def asin(x: np.ndarray)\
        -> np.ndarray:
    return np.arcsin(x)


def isinf(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.isinf(npa.asarray(x)))


def asinh(x: np.ndarray)\
        -> np.ndarray:
    return np.arcsinh(x)


def cosh(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.cosh(npa.asarray(x)))


def log10(x: np.ndarray)\
        -> np.ndarray:
    return np.log10(x)


def log(x: np.ndarray)\
        -> np.ndarray:
    return np.log(x)


def log2(x: np.ndarray)\
        -> np.ndarray:
    return np.log2(x)


def log1p(x: np.ndarray)\
        -> np.ndarray:
    return np.log1p(x)


def isnan(x: np.ndarray)\
        -> np.ndarray:
    return np.isnan(x)


def less(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return np.less(x1, x2)


def cos(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.cos(npa.asarray(x)))


def logical_not(x: np.ndarray)\
        -> np.ndarray:
    return np.logical_not(x)
  
  
def divide(x1: np.ndarray,
           x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    return npa.divide(npa.asarray(x1), npa.asarray(x2))


def acos(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.acos(npa.asarray(x)))


def logical_xor(x1: np.ndarray, x2: np.ndarray) \
        -> np.ndarray:
    return np.logical_xor(x1, x2)


def logical_or(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return np.logical_or(x1, x2)


def logical_and(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return np.logical_and(x1, x2)


def acosh(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.acosh(npa.asarray(x)))


def sin(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.sin(npa.asarray(x)))


def negative(x: np.ndarray) -> np.ndarray:
    return np.negative(x)


def not_equal(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    return np.not_equal(x1, x2)


def tanh(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.tanh(npa.asarray(x)))


def floor_divide(x1: np.ndarray, x2: np.ndarray)\
                -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    return npa.floor_divide(npa.asarray(x1), npa.asarray(x2))


def sinh(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.sinh(npa.asarray(x)))


def positive(x: np.ndarray)\
        -> np.ndarray:
    return np.positive(x)


def square(x: np.ndarray)\
        -> np.ndarray:
    return np.square(x)


def remainder(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.remainder(x1, x2)


def round(x: np.ndarray)\
        -> np.ndarray:
    return np.asarray(npa.round(npa.asarray(x)))


def bitwise_or(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.bitwise_or(x1, x2)


def trunc(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.trunc(npa.asarray(x)))


def abs(x: np.ndarray,
        out: Optional[np.ndarray] = None)\
        -> np.ndarray:
    return np.absolute(x, out=out)


def subtract(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if hasattr(x1, 'dtype') and hasattr(x2, 'dtype'):
        promoted_type = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(promoted_type)
        x2 = x2.astype(promoted_type)
    elif not hasattr(x2, 'dtype'):
        x2 = np.array(x2, dtype=x1.dtype)
    return np.subtract(x1, x2)


def logaddexp(x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.logaddexp(x1, x2)


def bitwise_right_shift(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.right_shift(x1, x2)


def bitwise_left_shift(x1: np.ndarray, x2: np.ndarray)\
        -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.left_shift(x1, x2)


tan = np.tan


def atan(x: np.ndarray) \
        -> np.ndarray:
    return np.arctan(x)




def atanh(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(np.arctanh(npa.asarray(x)))



def atan2(x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
    if not isinstance(x2, np.ndarray):
        x2 = np.asarray(x2, dtype=x1.dtype)
    else:
        dtype = np.promote_types(x1.dtype, x2.dtype)
        x1 = x1.astype(dtype)
        x2 = x2.astype(dtype)
    return np.arctan2(x1, x2)



cosh = np.cosh
log = np.log
exp = np.exp


# Extra #
# ------#


minimum = np.minimum
maximum = np.maximum


def erf(x):
    if _erf is None:
        raise Exception('scipy must be installed in order to call ivy.erf with a numpy backend.')
    return _erf(x)
