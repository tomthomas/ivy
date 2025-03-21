"""
Collection of tests for unified general functions
"""

# global
import copy
import pytest

# local
import ivy
import ivy.functional.backends.numpy


# Helpers #
# --------#

def _snai(n, idx, v):
    if len(idx) == 1:
        n[idx[0]] = v
    else:
        _snai(n[idx[0]], idx[1:], v)


def _mnai(n, idx, fn):
    if len(idx) == 1:
        n[idx[0]] = fn(n[idx[0]])
    else:
        _mnai(n[idx[0]], idx[1:], fn)


# Tests #
# ------#

# index_nest
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': (((2,), (4,)), ((6,), (8,)))}}])
@pytest.mark.parametrize(
    "index", [('a', 0, 0), ('a', 1, 0), ('b', 'c', 0), ('b', 'c', 1, 0)])
def test_index_nest(nest, index, dev, call):
    ret = ivy.index_nest(nest, index)
    true_ret = nest
    for i in index:
        true_ret = true_ret[i]
    assert ret == true_ret


# set_nest_at_index
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
@pytest.mark.parametrize(
    "index", [('a', 0, 0), ('a', 1, 0), ('b', 'c', 0), ('b', 'c', 1, 0)])
@pytest.mark.parametrize(
    "value", [1])
def test_set_nest_at_index(nest, index, value, dev, call):
    nest_copy = copy.deepcopy(nest)
    ivy.set_nest_at_index(nest, index, value)
    _snai(nest_copy, index, value)
    assert nest == nest_copy


# map_nest_at_index
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
@pytest.mark.parametrize(
    "index", [('a', 0, 0), ('a', 1, 0), ('b', 'c', 0, 0, 0), ('b', 'c', 1, 0, 0)])
@pytest.mark.parametrize(
    "fn", [lambda x: x + 2, lambda x: x**2])
def test_map_nest_at_index(nest, index, fn, dev, call):
    nest_copy = copy.deepcopy(nest)
    ivy.map_nest_at_index(nest, index, fn)
    _mnai(nest_copy, index, fn)
    assert nest == nest_copy


# multi_index_nest
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': (((2,), (4,)), ((6,), (8,)))}}])
@pytest.mark.parametrize(
    "multi_indices", [(('a', 0, 0), ('a', 1, 0)), (('b', 'c', 0), ('b', 'c', 1, 0))])
def test_multi_index_nest(nest, multi_indices, dev, call):
    rets = ivy.multi_index_nest(nest, multi_indices)
    true_rets = list()
    for indices in multi_indices:
        true_ret = nest
        for i in indices:
            true_ret = true_ret[i]
        true_rets.append(true_ret)
    assert rets == true_rets


# set_nest_at_indices
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
@pytest.mark.parametrize(
    "indices", [(('a', 0, 0), ('a', 1, 0)), (('b', 'c', 0), ('b', 'c', 1, 0))])
@pytest.mark.parametrize(
    "values", [(1, 2)])
def test_set_nest_at_indices(nest, indices, values, dev, call):
    nest_copy = copy.deepcopy(nest)
    ivy.set_nest_at_indices(nest, indices, values)

    def snais(n, idxs, vs):
        [_snai(n, index, value) for index, value in zip(idxs, vs)]

    snais(nest_copy, indices, values)

    assert nest == nest_copy


# map_nest_at_indices
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
@pytest.mark.parametrize(
    "indices", [(('a', 0, 0), ('a', 1, 0)), (('b', 'c', 0, 0, 0), ('b', 'c', 1, 0, 0))])
@pytest.mark.parametrize(
    "fn", [lambda x: x + 2, lambda x: x**2])
def test_map_nest_at_indices(nest, indices, fn, dev, call):
    nest_copy = copy.deepcopy(nest)
    ivy.map_nest_at_indices(nest, indices, fn)

    def mnais(n, idxs, vs):
        [_mnai(n, index, fn) for index in idxs]

    mnais(nest_copy, indices, fn)

    assert nest == nest_copy


# nested_indices_where
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
def test_nested_indices_where(nest, dev, call):
    indices = ivy.nested_indices_where(nest, lambda x: x < 5)
    assert indices[0] == ['a', 0, 0]
    assert indices[1] == ['a', 1, 0]
    assert indices[2] == ['b', 'c', 0, 0, 0]
    assert indices[3] == ['b', 'c', 0, 1, 0]


# nested_indices_where_w_nest_checks
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
def test_nested_indices_where_w_nest_checks(nest, dev, call):
    indices = ivy.nested_indices_where(nest, lambda x: isinstance(x, list) or (isinstance(x, int) and x < 5), True)
    assert indices[0] == ['a', 0, 0]
    assert indices[1] == ['a', 0]
    assert indices[2] == ['a', 1, 0]
    assert indices[3] == ['a', 1]
    assert indices[4] == ['a']
    assert indices[5] == ['b', 'c', 0, 0, 0]
    assert indices[6] == ['b', 'c', 0, 0]
    assert indices[7] == ['b', 'c', 0, 1, 0]
    assert indices[8] == ['b', 'c', 0, 1]
    assert indices[9] == ['b', 'c', 0]
    assert indices[10] == ['b', 'c', 1, 0]
    assert indices[11] == ['b', 'c', 1, 1]
    assert indices[12] == ['b', 'c', 1]
    assert indices[13] == ['b', 'c']


# all_nested_indices
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
def test_all_nested_indices(nest, dev, call):
    indices = ivy.all_nested_indices(nest)
    assert indices[0] == ['a', 0, 0]
    assert indices[1] == ['a', 1, 0]
    assert indices[2] == ['b', 'c', 0, 0, 0]
    assert indices[3] == ['b', 'c', 0, 1, 0]
    assert indices[4] == ['b', 'c', 1, 0, 0]
    assert indices[5] == ['b', 'c', 1, 1, 0]


# all_nested_indices_w_nest_checks
@pytest.mark.parametrize(
    "nest", [{'a': [[0], [1]], 'b': {'c': [[[2], [4]], [[6], [8]]]}}])
def test_all_nested_indices_w_nest_checks(nest, dev, call):
    indices = ivy.all_nested_indices(nest, True)
    assert indices[0] == ['a', 0, 0]
    assert indices[1] == ['a', 0]
    assert indices[2] == ['a', 1, 0]
    assert indices[3] == ['a', 1]
    assert indices[4] == ['a']
    assert indices[5] == ['b', 'c', 0, 0, 0]
    assert indices[6] == ['b', 'c', 0, 0]
    assert indices[7] == ['b', 'c', 0, 1, 0]
    assert indices[8] == ['b', 'c', 0, 1]
    assert indices[9] == ['b', 'c', 0]
    assert indices[10] == ['b', 'c', 1, 0, 0]
    assert indices[11] == ['b', 'c', 1, 0]
    assert indices[12] == ['b', 'c', 1, 1, 0]
    assert indices[13] == ['b', 'c', 1, 1]
    assert indices[14] == ['b', 'c', 1]
    assert indices[15] == ['b', 'c']
    assert indices[16] == ['b']


# copy_nest
def test_copy_nest(dev, call):

    nest = {'a': [ivy.array([0]), ivy.array([1])], 'b': {'c': [ivy.array([[2], [4]]), ivy.array([[6], [8]])]}}
    nest_copy = ivy.copy_nest(nest)

    # copied nests
    assert nest['a'] is not nest_copy['a']
    assert nest['b'] is not nest_copy['b']
    assert nest['b']['c'] is not nest_copy['b']['c']

    # non-copied arrays
    assert nest['a'][0] is nest_copy['a'][0]
    assert nest['a'][1] is nest_copy['a'][1]
    assert nest['b']['c'][0] is nest_copy['b']['c'][0]
    assert nest['b']['c'][1] is nest_copy['b']['c'][1]
