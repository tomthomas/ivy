# global
import numpy as np
from typing import Union, Optional, Tuple, Literal, List


# local
from ivy import inf
import ivy
from collections import namedtuple

# Array API Standard #
# -------------------#

def eigh(x: np.ndarray)\
  -> np.ndarray:
         return np.linalg.eigh(x)


def inv(x: np.ndarray) -> np.ndarray:
    return np.linalg.inv(x)


def pinv(x: np.ndarray,
         rtol: Optional[Union[float, Tuple[float]]] = None) \
        -> np.ndarray:

    if rtol is None:
        return np.linalg.pinv(x)
    return np.linalg.pinv(x, rtol)

def matrix_transpose(x: np.ndarray) \
        -> np.ndarray:
    return np.swapaxes(x, -1, -2)


# noinspection PyUnusedLocal,PyShadowingBuiltins
def vector_norm(x: np.ndarray,
                axis: Optional[Union[int, Tuple[int]]] = None,
                keepdims: bool = False,
                ord: Union[int, float, Literal[inf, - inf]] = 2) \
        -> np.ndarray:
    if axis is None:
        np_normalized_vector = np.linalg.norm(x.flatten(), ord, axis, keepdims)

    else:
        np_normalized_vector = np.linalg.norm(x, ord, axis, keepdims)

    if np_normalized_vector.shape == tuple():
        return np.expand_dims(np_normalized_vector, 0)
    return np_normalized_vector


def matrix_norm(x: np.ndarray,
                ord: Optional[Union[int, float, Literal[inf, - inf, 'fro', 'nuc']]] = 'fro',
                keepdims: bool = False)\
        -> np.ndarray:
    return np.linalg.norm(x, ord=ord, axis=(-2, -1), keepdims=keepdims)


def svd(x: np.ndarray, full_matrices: bool = True) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
    results = namedtuple("svd", "U S Vh")
    U, D, VT = np.linalg.svd(x, full_matrices=full_matrices)
    res = results(U, D, VT)
    return res


def outer(x1: np.ndarray,
          x2: np.ndarray)\
        -> np.ndarray:
    return np.outer(x1, x2)


def diagonal(x: np.ndarray,
             offset: int = 0,
             axis1: int = -2,
             axis2: int = -1) -> np.ndarray:
    return np.diagonal(x, offset=offset, axis1=axis1, axis2=axis2)


def svdvals(x: np.ndarray) -> np.ndarray:
    return np.linalg.svd(x, compute_uv=False)


def qr(x: np.ndarray,
       mode: str = 'reduced') -> namedtuple('qr', ['Q', 'R']):
    res = namedtuple('qr', ['Q', 'R'])
    q, r = np.linalg.qr(x, mode=mode)
    return res(q, r)


def matmul(x1: np.ndarray,
           x2: np.ndarray) -> np.ndarray:
    return np.matmul(x1, x2)


def slogdet(x: Union[ivy.Array, ivy.NativeArray], full_matrices: bool = True) -> Union[
    ivy.Array, Tuple[ivy.Array, ...]]:
    results = namedtuple("slogdet", "sign logabsdet")
    sign, logabsdet = np.linalg.slogdet(x)
    res = results(sign, logabsdet)
    return res

def tensordot(x1: np.ndarray, x2: np.ndarray,
              axes: Union[int, Tuple[List[int], List[int]]] = 2) \
    -> np.ndarray:

    return np.tensordot(x1, x2, axes=axes)


def trace(x: np.ndarray,
          offset: int = 0) \
        -> np.ndarray:
    return np.trace(x, offset)


def vecdot(x1: np.ndarray, 
           x2: np.ndarray,
           axis: int = -1)\
        -> np.ndarray:
    return np.tensordot(x1, x2, axes=(axis, axis))


def det(x: np.array) \
        -> np.array:
    return np.linalg.det(x)


def cholesky(x: np.ndarray,
             upper: bool = False) -> np.ndarray:
    if not upper:
        return np.linalg.cholesky(x)
    else:
        axes = list(range(len(x.shape)-2))+[len(x.shape)-1, len(x.shape)-2]
        return np.transpose(np.linalg.cholesky(np.transpose(x, axes=axes)),
                            axes=axes)

def eigvalsh(x: np.ndarray) -> np.ndarray:
    return np.linalg.eigvalsh(x)

def cross (x1: np.ndarray,
           x2: np.ndarray,
           axis:int = -1) -> np.ndarray:
    return np.cross(a= x1, b = x2, axis= axis)


def matrix_rank(vector: np.ndarray,
                rtol: Optional[Union[float, Tuple[float]]] = None) \
        -> np.ndarray:
    if rtol is None:
        return np.linalg.matrix_rank(vector)
    return np.linalg.matrix_rank(vector, rtol)

# Extra #
# ------#

def vector_to_skew_symmetric_matrix(vector: np.ndarray) \
        -> np.ndarray:
    batch_shape = list(vector.shape[:-1])
    # BS x 3 x 1
    vector_expanded = np.expand_dims(vector, -1)
    # BS x 1 x 1
    a1s = vector_expanded[..., 0:1, :]
    a2s = vector_expanded[..., 1:2, :]
    a3s = vector_expanded[..., 2:3, :]
    # BS x 1 x 1
    zs = np.zeros(batch_shape + [1, 1])
    # BS x 1 x 3
    row1 = np.concatenate((zs, -a3s, a2s), -1)
    row2 = np.concatenate((a3s, zs, -a1s), -1)
    row3 = np.concatenate((-a2s, a1s, zs), -1)
    # BS x 3 x 3
    return np.concatenate((row1, row2, row3), -2)
