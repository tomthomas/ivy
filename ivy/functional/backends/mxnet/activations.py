"""
Collection of MXNet activation functions, wrapped to fit Ivy syntax and signature.
"""

from typing import Optional

# global
import numpy as _np
import mxnet as _mx


def relu(x: _mx.nd.NDArray)\
        -> _mx.nd.NDArray:
    return _mx.nd.relu(x)


def leaky_relu(x: _mx.nd.NDArray, alpha: Optional[float] = 0.2)\
        -> _mx.nd.NDArray:
    return _mx.nd.LeakyReLU(x, slope=alpha)


def gelu(x, approximate=True):
    if approximate:
        return 0.5 * x * (1 + _mx.nd.tanh(((2 / _np.pi) ** 0.5) * (x + 0.044715 * x ** 3)))
    return _mx.nd.LeakyReLU(x, act_type='gelu')


tanh = _mx.nd.tanh
sigmoid = _mx.nd.sigmoid
softmax = lambda x, axis=-1: _mx.nd.softmax(x, axis=axis)
softplus = lambda x: _mx.nd.log(_mx.nd.exp(x) + 1)
