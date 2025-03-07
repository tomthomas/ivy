# global
import jax
import jax.numpy as jnp
from typing import Union, Optional, Tuple, Literal, List
from collections import namedtuple

# local
from ivy import inf
from ivy.functional.backends.jax import JaxArray
import ivy


# Array API Standard #
# -------------------#

def eigh(x: JaxArray)\
  ->JaxArray:
         return jnp.linalg.eigh(x)

def pinv(x: JaxArray,
         rtol: Optional[Union[float, Tuple[float]]] = None) \
        -> JaxArray:

    if rtol is None:
        return jnp.linalg.pinv(x)
    return jnp.linalg.pinv(x, rtol)


def matrix_transpose(x: JaxArray)\
        -> JaxArray:
    return jnp.swapaxes(x, -1, -2)


# noinspection PyUnusedLocal,PyShadowingBuiltins
def vector_norm(x: JaxArray,
                axis: Optional[Union[int, Tuple[int]]] = None, 
                keepdims: bool = False,
                ord: Union[int, float, Literal[inf, -inf]] = 2)\
        -> JaxArray:

    if axis is None:
        jnp_normalized_vector = jnp.linalg.norm(jnp.ravel(x), ord, axis, keepdims)
    else:
        jnp_normalized_vector = jnp.linalg.norm(x, ord, axis, keepdims)

    if jnp_normalized_vector.shape == ():
        return jnp.expand_dims(jnp_normalized_vector, 0)
    return jnp_normalized_vector


def matrix_norm(x: JaxArray,
                ord: Optional[Union[int, float, Literal[inf, - inf, 'fro', 'nuc']]] = 'fro',
                keepdims: bool = False)\
        -> JaxArray:
    if x.size == 0:
        if keepdims:
            return x.reshape(x.shape[:-2] + (1, 1))
        else:
            return x.reshape(x.shape[:-2])
    return jnp.linalg.norm(x, ord, (-2, -1), keepdims)


def svd(x: JaxArray, full_matrices: bool = True) -> Union[JaxArray, Tuple[JaxArray,...]]:
    results = namedtuple("svd", "U S Vh")
    U, D, VT = jnp.linalg.svd(x, full_matrices=full_matrices)
    res = results(U, D, VT)
    return res


def outer(x1: JaxArray,
          x2: JaxArray)\
        -> JaxArray:
    return jnp.outer(x1, x2)


def diagonal(x: JaxArray,
             offset: int = 0,
             axis1: int = -2,
             axis2: int = -1) -> JaxArray:
    return jnp.diagonal(x, offset, axis1, axis2)


def svdvals(x: JaxArray) -> JaxArray:
    return jnp.linalg.svd(x, compute_uv=False)


def qr(x: JaxArray,
       mode: str = 'reduced') -> namedtuple('qr', ['Q', 'R']):
    res = namedtuple('qr', ['Q', 'R'])
    q, r = jnp.linalg.qr(x, mode=mode)
    return res(q, r)


def matmul(x1: JaxArray,
           x2: JaxArray) -> JaxArray:
    return jnp.matmul(x1, x2)


def slogdet(x:Union[ivy.Array,ivy.NativeArray],full_matrices: bool = True) -> Union[ivy.Array, Tuple[ivy.Array,...]]:
    results = namedtuple("slogdet", "sign logabsdet")
    sign, logabsdet = jnp.linalg.slogdet(x)
    res = results(sign, logabsdet)
    return res

def tensordot(x1: JaxArray, x2: JaxArray,
              axes: Union[int, Tuple[List[int], List[int]]] = 2) \
        -> JaxArray:

    return jnp.tensordot(x1, x2, axes)


def trace(x: JaxArray,
          offset: int = 0)\
              -> JaxArray:
    return jax.numpy.trace(x, offset)


def det(x:jnp.array) \
    -> jnp.array:
    return jnp.linalg.det(x)

def cholesky(x: JaxArray, 
             upper: bool = False) -> JaxArray:
    if not upper:
        return jnp.linalg.cholesky(x)
    else:
        axes = list(range(len(x.shape) - 2)) + [len(x.shape) - 1, len(x.shape) - 2]
        return jnp.transpose(jnp.linalg.cholesky(jnp.transpose(x, axes=axes)),
                        axes=axes)


def eigvalsh(x: JaxArray) -> JaxArray:
    return jnp.linalg.eigvalsh(x)


def inv(x: JaxArray) -> JaxArray:
    if jnp.any(jnp.linalg.det(x.astype('float64')) == 0):
        return x
    return jnp.linalg.inv(x)


def matrix_rank(vector: JaxArray,
                rtol: Optional[Union[float, Tuple[float]]] = None) \
        -> JaxArray:
        if vector.size == 0:
            return 0
        if vector.size == 1:
            return jnp.count_nonzero(vector)
        if vector.ndim >2:
            vector = vector.reshape([-1])
        return jnp.linalg.matrix_rank(vector, rtol)


def cross (x1: JaxArray,
           x2: JaxArray,
           axis:int = -1) -> JaxArray:
    return jnp.cross(a= x1, b = x2, axis= axis)


def vecdot(x1: JaxArray,
           x2: JaxArray,
           axis: int = -1)\
        -> JaxArray:
    return jnp.tensordot(x1, x2, (axis, axis))


# Extra #
# ------#

def vector_to_skew_symmetric_matrix(vector: JaxArray)\
        -> JaxArray:
    batch_shape = list(vector.shape[:-1])
    # BS x 3 x 1
    vector_expanded = jnp.expand_dims(vector, -1)
    # BS x 1 x 1
    a1s = vector_expanded[..., 0:1, :]
    a2s = vector_expanded[..., 1:2, :]
    a3s = vector_expanded[..., 2:3, :]
    # BS x 1 x 1
    zs = jnp.zeros(batch_shape + [1, 1])
    # BS x 1 x 3
    row1 = jnp.concatenate((zs, -a3s, a2s), -1)
    row2 = jnp.concatenate((a3s, zs, -a1s), -1)
    row3 = jnp.concatenate((-a2s, a1s, zs), -1)
    # BS x 3 x 3
    return jnp.concatenate((row1, row2, row3), -2)

