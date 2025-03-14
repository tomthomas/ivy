# global
import os
import queue
import pickle
import pytest
import random
import numpy as np
import multiprocessing

# local
import ivy
from ivy.container import Container
import ivy_tests.test_ivy.helpers as helpers


def test_container_list_join(dev, call):
    container_0 = Container({'a': [ivy.array([1], dev=dev)],
                             'b': {'c': [ivy.array([2], dev=dev)], 'd': [ivy.array([3], dev=dev)]}})
    container_1 = Container({'a': [ivy.array([4], dev=dev)],
                             'b': {'c': [ivy.array([5], dev=dev)], 'd': [ivy.array([6], dev=dev)]}})
    container_list_joined = ivy.Container.list_join([container_0, container_1])
    assert np.allclose(ivy.to_numpy(container_list_joined['a'][0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_list_joined.a[0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_list_joined['b']['c'][0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_list_joined.b.c[0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_list_joined['b']['d'][0]), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_list_joined.b.d[0]), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_list_joined['a'][1]), np.array([4]))
    assert np.allclose(ivy.to_numpy(container_list_joined.a[1]), np.array([4]))
    assert np.allclose(ivy.to_numpy(container_list_joined['b']['c'][1]), np.array([5]))
    assert np.allclose(ivy.to_numpy(container_list_joined.b.c[1]), np.array([5]))
    assert np.allclose(ivy.to_numpy(container_list_joined['b']['d'][1]), np.array([6]))
    assert np.allclose(ivy.to_numpy(container_list_joined.b.d[1]), np.array([6]))


def test_container_list_stack(dev, call):
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_list_stacked = ivy.Container.list_stack([container_0, container_1], 0)
    assert np.allclose(ivy.to_numpy(container_list_stacked['a'][0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.a[0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_list_stacked['b']['c'][0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.b.c[0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_list_stacked['b']['d'][0]), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.b.d[0]), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_list_stacked['a'][1]), np.array([4]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.a[1]), np.array([4]))
    assert np.allclose(ivy.to_numpy(container_list_stacked['b']['c'][1]), np.array([5]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.b.c[1]), np.array([5]))
    assert np.allclose(ivy.to_numpy(container_list_stacked['b']['d'][1]), np.array([6]))
    assert np.allclose(ivy.to_numpy(container_list_stacked.b.d[1]), np.array([6]))


def test_container_unify(dev, call):

    # devices and containers
    devs = list()
    dev0 = dev
    devs.append(dev0)
    conts = dict()
    conts[dev0] = Container(
        {'a': ivy.array([1], dev=dev0),
         'b': {'c': ivy.array([2], dev=dev0), 'd': ivy.array([3], dev=dev0)}})
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)
        conts[dev1] = Container(
            {'a': ivy.array([4], dev=dev1),
             'b': {'c': ivy.array([5], dev=dev1), 'd': ivy.array([6], dev=dev1)}})

    # test
    container_unified = ivy.Container.unify(ivy.MultiDevItem(conts), dev0, 'concat', 0)
    assert np.allclose(ivy.to_numpy(container_unified.a[0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_unified.b.c[0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_unified.b.d[0]), np.array([3]))
    if len(devs) > 1:
        assert np.allclose(ivy.to_numpy(container_unified.a[1]), np.array([4]))
        assert np.allclose(ivy.to_numpy(container_unified.b.c[1]), np.array([5]))
        assert np.allclose(ivy.to_numpy(container_unified.b.d[1]), np.array([6]))


def test_container_concat(dev, call):
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_concatenated = ivy.Container.concat([container_0, container_1], 0)
    assert np.allclose(ivy.to_numpy(container_concatenated['a']), np.array([1, 4]))
    assert np.allclose(ivy.to_numpy(container_concatenated.a), np.array([1, 4]))
    assert np.allclose(ivy.to_numpy(container_concatenated['b']['c']), np.array([2, 5]))
    assert np.allclose(ivy.to_numpy(container_concatenated.b.c), np.array([2, 5]))
    assert np.allclose(ivy.to_numpy(container_concatenated['b']['d']), np.array([3, 6]))
    assert np.allclose(ivy.to_numpy(container_concatenated.b.d), np.array([3, 6]))


def test_container_stack(dev, call):
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_stacked = ivy.Container.stack([container_0, container_1], 0)
    assert np.allclose(ivy.to_numpy(container_stacked['a']), np.array([[1], [4]]))
    assert np.allclose(ivy.to_numpy(container_stacked.a), np.array([[1], [4]]))
    assert np.allclose(ivy.to_numpy(container_stacked['b']['c']), np.array([[2], [5]]))
    assert np.allclose(ivy.to_numpy(container_stacked.b.c), np.array([[2], [5]]))
    assert np.allclose(ivy.to_numpy(container_stacked['b']['d']), np.array([[3], [6]]))
    assert np.allclose(ivy.to_numpy(container_stacked.b.d), np.array([[3], [6]]))


def test_container_combine(dev, call):
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'e': ivy.array([6], dev=dev)}})
    container_comb = ivy.Container.combine(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_comb.a), np.array([4]))
    assert np.equal(ivy.to_numpy(container_comb.b.c), np.array([5]))
    assert np.equal(ivy.to_numpy(container_comb.b.d), np.array([3]))
    assert np.equal(ivy.to_numpy(container_comb.b.e), np.array([6]))


def test_container_diff(dev, call):
    # all different arrays
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a.diff_0), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.a.diff_1), np.array([4]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_0), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_1), np.array([5]))
    assert np.equal(ivy.to_numpy(container_diff.b.d.diff_0), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.b.d.diff_1), np.array([6]))
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == container_diff.to_dict()
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == {}

    # some different arrays
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_0), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_1), np.array([5]))
    assert np.equal(ivy.to_numpy(container_diff.b.d), np.array([3]))
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert 'a' not in container_diff_diff_only
    assert 'b' in container_diff_diff_only
    assert 'c' in container_diff_diff_only['b']
    assert 'd' not in container_diff_diff_only['b']
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert 'a' in container_diff_same_only
    assert 'b' in container_diff_same_only
    assert 'c' not in container_diff_same_only['b']
    assert 'd' in container_diff_same_only['b']

    # all different keys
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'e': ivy.array([1], dev=dev),
                             'f': {'g': ivy.array([2], dev=dev), 'h': ivy.array([3], dev=dev)}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a.diff_0), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.diff_0.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.diff_0.d), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.e.diff_1), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.f.diff_1.g), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.f.diff_1.h), np.array([3]))
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == container_diff.to_dict()
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == {}

    # some different keys
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'e': ivy.array([3], dev=dev)}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.d.diff_0), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.b.e.diff_1), np.array([3]))
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert 'a' not in container_diff_diff_only
    assert 'b' in container_diff_diff_only
    assert 'c' not in container_diff_diff_only['b']
    assert 'd' in container_diff_diff_only['b']
    assert 'e' in container_diff_diff_only['b']
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert 'a' in container_diff_same_only
    assert 'b' in container_diff_same_only
    assert 'c' in container_diff_same_only['b']
    assert 'd' not in container_diff_same_only['b']
    assert 'e' not in container_diff_same_only['b']

    # same containers
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.d), np.array([3]))
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == {}
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == container_diff.to_dict()

    # all different strings
    container_0 = Container({'a': '1',
                             'b': {'c': '2', 'd': '3'}})
    container_1 = Container({'a': '4',
                             'b': {'c': '5', 'd': '6'}})
    container_diff = ivy.Container.diff(container_0, container_1)
    assert container_diff.a.diff_0 == '1'
    assert container_diff.a.diff_1 == '4'
    assert container_diff.b.c.diff_0 == '2'
    assert container_diff.b.c.diff_1 == '5'
    assert container_diff.b.d.diff_0 == '3'
    assert container_diff.b.d.diff_1 == '6'
    container_diff_diff_only = ivy.Container.diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == container_diff.to_dict()
    container_diff_same_only = ivy.Container.diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == {}


def test_container_structural_diff(dev, call):
    # all different keys or shapes
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([[4]], dev=dev),
                             'b': {'c': ivy.array([[[5]]], dev=dev), 'e': ivy.array([3], dev=dev)}})
    container_diff = ivy.Container.structural_diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a.diff_0), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.a.diff_1), np.array([[4]]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_0), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_1), np.array([[[5]]]))
    assert np.equal(ivy.to_numpy(container_diff.b.d.diff_0), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.b.e.diff_1), np.array([3]))
    container_diff_diff_only = ivy.Container.structural_diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == container_diff.to_dict()
    container_diff_same_only = ivy.Container.structural_diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == {}

    # some different shapes
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([[5]], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_diff = ivy.Container.structural_diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_0), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.c.diff_1), np.array([5]))
    assert np.equal(ivy.to_numpy(container_diff.b.d), np.array([3]))
    container_diff_diff_only = ivy.Container.structural_diff(container_0, container_1, mode='diff_only')
    assert 'a' not in container_diff_diff_only
    assert 'b' in container_diff_diff_only
    assert 'c' in container_diff_diff_only['b']
    assert 'd' not in container_diff_diff_only['b']
    container_diff_same_only = ivy.Container.structural_diff(container_0, container_1, mode='same_only')
    assert 'a' in container_diff_same_only
    assert 'b' in container_diff_same_only
    assert 'c' not in container_diff_same_only['b']
    assert 'd' in container_diff_same_only['b']

    # all different keys
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'e': ivy.array([4], dev=dev),
                             'f': {'g': ivy.array([5], dev=dev), 'h': ivy.array([6], dev=dev)}})
    container_diff = ivy.Container.structural_diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a.diff_0), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.diff_0.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.diff_0.d), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.e.diff_1), np.array([4]))
    assert np.equal(ivy.to_numpy(container_diff.f.diff_1.g), np.array([5]))
    assert np.equal(ivy.to_numpy(container_diff.f.diff_1.h), np.array([6]))
    container_diff_diff_only = ivy.Container.structural_diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == container_diff.to_dict()
    container_diff_same_only = ivy.Container.structural_diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == {}

    # some different keys
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'e': ivy.array([6], dev=dev)}})
    container_diff = ivy.Container.structural_diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.d.diff_0), np.array([3]))
    assert np.equal(ivy.to_numpy(container_diff.b.e.diff_1), np.array([6]))
    container_diff_diff_only = ivy.Container.structural_diff(container_0, container_1, mode='diff_only')
    assert 'a' not in container_diff_diff_only
    assert 'b' in container_diff_diff_only
    assert 'c' not in container_diff_diff_only['b']
    assert 'd' in container_diff_diff_only['b']
    assert 'e' in container_diff_diff_only['b']
    container_diff_same_only = ivy.Container.structural_diff(container_0, container_1, mode='same_only')
    assert 'a' in container_diff_same_only
    assert 'b' in container_diff_same_only
    assert 'c' in container_diff_same_only['b']
    assert 'd' not in container_diff_same_only['b']
    assert 'e' not in container_diff_same_only['b']

    # all same
    container_0 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_1 = Container({'a': ivy.array([4], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_diff = ivy.Container.structural_diff(container_0, container_1)
    assert np.equal(ivy.to_numpy(container_diff.a), np.array([1]))
    assert np.equal(ivy.to_numpy(container_diff.b.c), np.array([2]))
    assert np.equal(ivy.to_numpy(container_diff.b.d), np.array([3]))
    container_diff_diff_only = ivy.Container.structural_diff(container_0, container_1, mode='diff_only')
    assert container_diff_diff_only.to_dict() == {}
    container_diff_same_only = ivy.Container.structural_diff(container_0, container_1, mode='same_only')
    assert container_diff_same_only.to_dict() == container_diff.to_dict()


def test_container_from_dict(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([3]))


def test_container_depth(dev, call):
    cont_depth1 = Container({'a': ivy.array([1], dev=dev),
                             'b': ivy.array([2], dev=dev)})
    assert cont_depth1.max_depth == 1
    cont_depth2 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    assert cont_depth2.max_depth == 2
    cont_depth3 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': {'d': ivy.array([2], dev=dev)}, 'e': ivy.array([3], dev=dev)}})
    assert cont_depth3.max_depth == 3
    cont_depth4 = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': {'d': {'e': ivy.array([2], dev=dev)}}}})
    assert cont_depth4.max_depth == 4


@pytest.mark.parametrize(
    "inplace", [True, False])
def test_container_cutoff_at_depth(inplace, dev, call):

    # values
    a_val = ivy.array([1], dev=dev)
    bcde_val = ivy.array([2], dev=dev)

    # depth 1
    cont = Container({'a': a_val, 'b': {'c': {'d': {'e': bcde_val}}}})
    cont_cutoff = cont.cutoff_at_depth(1, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert np.allclose(ivy.to_numpy(cont_cutoff.a), ivy.to_numpy(a_val))
    assert not cont_cutoff.b

    # depth 2
    cont = Container({'a': a_val, 'b': {'c': {'d': {'e': bcde_val}}}})
    cont_cutoff = cont.cutoff_at_depth(2, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert np.allclose(ivy.to_numpy(cont_cutoff.a), ivy.to_numpy(a_val))
    assert not cont_cutoff.b.c

    # depth 3
    cont = Container({'a': a_val, 'b': {'c': {'d': {'e': bcde_val}}}})
    cont_cutoff = cont.cutoff_at_depth(3, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert np.allclose(ivy.to_numpy(cont_cutoff.a), ivy.to_numpy(a_val))
    assert not cont_cutoff.b.c.d

    # depth 4
    cont = Container({'a': a_val, 'b': {'c': {'d': {'e': bcde_val}}}})
    cont_cutoff = cont.cutoff_at_depth(4, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert np.allclose(ivy.to_numpy(cont_cutoff.a), ivy.to_numpy(a_val))
    assert np.allclose(ivy.to_numpy(cont_cutoff.b.c.d.e), ivy.to_numpy(bcde_val))


@pytest.mark.parametrize(
    "inplace", [True, False])
def test_container_cutoff_at_height(inplace, dev, call):

    # values
    d_val = ivy.array([2], dev=dev)
    e_val = ivy.array([3], dev=dev)

    # height 0
    cont = Container({'a': {'c': {'d': d_val}}, 'b': {'c': {'d': {'e': e_val}}}})
    cont_cutoff = cont.cutoff_at_height(0, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert np.allclose(ivy.to_numpy(cont_cutoff.a.c.d), ivy.to_numpy(d_val))
    assert np.allclose(ivy.to_numpy(cont_cutoff.b.c.d.e), ivy.to_numpy(e_val))

    # height 1
    cont = Container({'a': {'c': {'d': d_val}}, 'b': {'c': {'d': {'e': e_val}}}})
    cont_cutoff = cont.cutoff_at_height(1, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert not cont_cutoff.a.c
    assert not cont_cutoff.b.c.d

    # height 2
    cont = Container({'a': {'c': {'d': d_val}}, 'b': {'c': {'d': {'e': e_val}}}})
    cont_cutoff = cont.cutoff_at_height(2, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert not cont_cutoff.a
    assert not cont_cutoff.b.c

    # height 3
    cont = Container({'a': {'c': {'d': d_val}}, 'b': {'c': {'d': {'e': e_val}}}})
    cont_cutoff = cont.cutoff_at_height(3, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert not cont_cutoff.a
    assert not cont_cutoff.b

    # height 4
    cont = Container({'a': {'c': {'d': d_val}}, 'b': {'c': {'d': {'e': e_val}}}})
    cont_cutoff = cont.cutoff_at_height(4, inplace=inplace)
    if inplace:
        cont_cutoff = cont
    assert not cont_cutoff


@pytest.mark.parametrize(
    "str_slice", [True, False])
def test_container_slice_keys(str_slice, dev, call):

    # values
    a_val = ivy.array([1], dev=dev)
    b_val = ivy.array([2], dev=dev)
    c_val = ivy.array([3], dev=dev)
    d_val = ivy.array([4], dev=dev)
    e_val = ivy.array([5], dev=dev)

    # slice
    if str_slice:
        slc = 'b:d'
    else:
        slc = slice(1, 4, 1)

    # without dict
    cont = Container({'a': a_val, 'b': b_val, 'c': c_val, 'd': d_val, 'e': e_val})
    cont_sliced = cont.slice_keys(slc)
    assert 'a' not in cont_sliced
    assert np.allclose(ivy.to_numpy(cont_sliced.b), ivy.to_numpy(b_val))
    assert np.allclose(ivy.to_numpy(cont_sliced.c), ivy.to_numpy(c_val))
    assert np.allclose(ivy.to_numpy(cont_sliced.d), ivy.to_numpy(d_val))
    assert 'e' not in cont_sliced

    # with dict, depth 0
    sub_cont = Container({'a': a_val, 'b': b_val, 'c': c_val, 'd': d_val, 'e': e_val})
    cont = Container({'a': sub_cont, 'b': sub_cont, 'c': sub_cont, 'd': sub_cont, 'e': sub_cont})
    cont_sliced = cont.slice_keys({0: slc})
    assert 'a' not in cont_sliced
    assert Container.identical([cont_sliced.b, sub_cont])
    assert Container.identical([cont_sliced.c, sub_cont])
    assert Container.identical([cont_sliced.d, sub_cont])
    assert 'e' not in cont_sliced

    # with dict, depth 1
    sub_cont = Container({'a': a_val, 'b': b_val, 'c': c_val, 'd': d_val, 'e': e_val})
    sub_sub_cont = Container({'b': b_val, 'c': c_val, 'd': d_val})
    cont = Container({'a': sub_cont, 'b': sub_cont, 'c': sub_cont, 'd': sub_cont, 'e': sub_cont})
    cont_sliced = cont.slice_keys({1: slc})
    assert Container.identical([cont_sliced.a, sub_sub_cont])
    assert Container.identical([cont_sliced.b, sub_sub_cont])
    assert Container.identical([cont_sliced.c, sub_sub_cont])
    assert Container.identical([cont_sliced.d, sub_sub_cont])
    assert Container.identical([cont_sliced.e, sub_sub_cont])

    # with dict, depth 0, 1
    sub_cont = Container({'a': a_val, 'b': b_val, 'c': c_val, 'd': d_val, 'e': e_val})
    sub_sub_cont = Container({'b': b_val, 'c': c_val, 'd': d_val})
    cont = Container({'a': sub_cont, 'b': sub_cont, 'c': sub_cont, 'd': sub_cont, 'e': sub_cont})
    cont_sliced = cont.slice_keys({0: slc, 1: slc})
    assert 'a' not in cont_sliced
    assert Container.identical([cont_sliced.b, sub_sub_cont])
    assert Container.identical([cont_sliced.c, sub_sub_cont])
    assert Container.identical([cont_sliced.d, sub_sub_cont])
    assert 'e' not in cont_sliced

    # all depths
    sub_cont = Container({'a': a_val, 'b': b_val, 'c': c_val, 'd': d_val, 'e': e_val})
    sub_sub_cont = Container({'b': b_val, 'c': c_val, 'd': d_val})
    cont = Container({'a': sub_cont, 'b': sub_cont, 'c': sub_cont, 'd': sub_cont, 'e': sub_cont})
    cont_sliced = cont.slice_keys(slc, all_depths=True)
    assert 'a' not in cont_sliced
    assert Container.identical([cont_sliced.b, sub_sub_cont])
    assert Container.identical([cont_sliced.c, sub_sub_cont])
    assert Container.identical([cont_sliced.d, sub_sub_cont])
    assert 'e' not in cont_sliced


def test_container_show(dev, call):
    if call is helpers.mx_call:
        # ToDo: get this working for mxnet again, recent version update caused errors.
        pytest.skip()
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    cont = Container(dict_in)
    print(cont)
    cont.show()


def test_container_find_sub_container(dev, call):
    arr1 = ivy.array([1], dev=dev)
    arr2 = ivy.array([2], dev=dev)
    arr3 = ivy.array([3], dev=dev)
    dict_in = {'a': arr1, 'b': {'c': arr2, 'd': arr3}}
    top_cont = Container(dict_in)

    # full
    sub_cont = Container(dict_in['b'])
    assert sub_cont in top_cont
    found_kc = top_cont.find_sub_container(sub_cont)
    assert found_kc == 'b'
    found_kc = top_cont.find_sub_container(top_cont)
    assert found_kc == ''

    # partial
    partial_sub_cont = Container({'d': arr3})
    found_kc = top_cont.find_sub_container(partial_sub_cont, partial=True)
    assert found_kc == 'b'
    assert partial_sub_cont.find_sub_container(top_cont, partial=True) is False
    partial_sub_cont = Container({'b': {'d': arr3}})
    found_kc = top_cont.find_sub_container(partial_sub_cont, partial=True)
    assert found_kc == ''
    assert partial_sub_cont.find_sub_container(top_cont, partial=True) is False


def test_container_find_sub_structure(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    top_cont = Container(dict_in)

    # full
    sub_cont = Container({'c': ivy.array([4], dev=dev), 'd': ivy.array([5], dev=dev)})
    assert not top_cont.find_sub_container(sub_cont)
    found_kc = top_cont.find_sub_structure(sub_cont)
    assert found_kc == 'b'
    found_kc = top_cont.find_sub_structure(top_cont)
    assert found_kc == ''

    # partial
    partial_sub_cont = Container({'d': ivy.array([5], dev=dev)})
    found_kc = top_cont.find_sub_structure(partial_sub_cont, partial=True)
    assert found_kc == 'b'
    partial_sub_cont = Container({'b': {'d': ivy.array([5], dev=dev)}})
    found_kc = top_cont.find_sub_structure(partial_sub_cont, partial=True)
    assert found_kc == ''


def test_container_show_sub_container(dev, call):
    if call is helpers.mx_call:
        # ToDo: get this working for mxnet again, recent version update caused errors.
        pytest.skip()
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    top_cont = Container(dict_in)
    sub_cont = Container(dict_in['b'])
    top_cont.show_sub_container('b')
    top_cont.show_sub_container(sub_cont)


def test_container_from_dict_w_cont_types(dev, call):
    # ToDo: add tests for backends other than jax
    if call is not helpers.jnp_call:
        pytest.skip()
    from haiku._src.data_structures import FlatMapping
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': FlatMapping({'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)})}
    container = Container(dict_in)
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([3]))


def test_container_from_kwargs(dev, call):
    container = Container(a=ivy.array([1], dev=dev),
                          b={'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([3]))


def test_container_from_list(dev, call):
    list_in = [ivy.array([1], dev=dev),
               [ivy.array([2], dev=dev), ivy.array([3], dev=dev)]]
    container = Container(list_in, types_to_iteratively_nest=[list])
    assert np.allclose(ivy.to_numpy(container['it_0']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.it_0), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['it_1']['it_0']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.it_1.it_0), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['it_1']['it_1']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.it_1.it_1), np.array([3]))


def test_container_from_tuple(dev, call):
    tuple_in = (ivy.array([1], dev=dev),
               (ivy.array([2], dev=dev), ivy.array([3], dev=dev)))
    container = Container(tuple_in, types_to_iteratively_nest=[tuple])
    assert np.allclose(ivy.to_numpy(container['it_0']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.it_0), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['it_1']['it_0']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.it_1.it_0), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['it_1']['it_1']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.it_1.it_1), np.array([3]))


def test_container_to_raw(dev, call):
    tuple_in = (ivy.array([1], dev=dev),
               (ivy.array([2], dev=dev), ivy.array([3], dev=dev)))
    container = Container(tuple_in, types_to_iteratively_nest=[tuple])
    raw = container.to_raw()
    assert np.allclose(ivy.to_numpy(raw[0]), np.array([1]))
    assert np.allclose(ivy.to_numpy(raw[1][0]), np.array([2]))
    assert np.allclose(ivy.to_numpy(raw[1][1]), np.array([3]))

def test_container_sum(dev, call):
    dict_in = {'a': ivy.array([1., 2., 3.], dev=dev),
               'b': {'c': ivy.array([2., 4., 6.], dev=dev), 'd': ivy.array([3., 6., 9.], dev=dev)}}
    container = Container(dict_in)
    container_sum = container.sum()
    assert np.allclose(ivy.to_numpy(container_sum['a']), np.array([6.]))
    assert np.allclose(ivy.to_numpy(container_sum.a), np.array([6.]))
    assert np.allclose(ivy.to_numpy(container_sum['b']['c']), np.array([12.]))
    assert np.allclose(ivy.to_numpy(container_sum.b.c), np.array([12.]))
    assert np.allclose(ivy.to_numpy(container_sum['b']['d']), np.array([18.]))
    assert np.allclose(ivy.to_numpy(container_sum.b.d), np.array([18.]))


def test_container_prod(dev, call):
    dict_in = {'a': ivy.array([1., 2., 3.], dev=dev),
               'b': {'c': ivy.array([2., 4., 6.], dev=dev), 'd': ivy.array([3., 6., 9.], dev=dev)}}
    container = Container(dict_in)
    container_prod = container.prod()
    assert np.allclose(ivy.to_numpy(container_prod['a']), np.array([6.]))
    assert np.allclose(ivy.to_numpy(container_prod.a), np.array([6.]))
    assert np.allclose(ivy.to_numpy(container_prod['b']['c']), np.array([48.]))
    assert np.allclose(ivy.to_numpy(container_prod.b.c), np.array([48.]))
    assert np.allclose(ivy.to_numpy(container_prod['b']['d']), np.array([162.]))
    assert np.allclose(ivy.to_numpy(container_prod.b.d), np.array([162.]))


def test_container_mean(dev, call):
    dict_in = {'a': ivy.array([1., 2., 3.], dev=dev),
               'b': {'c': ivy.array([2., 4., 6.], dev=dev), 'd': ivy.array([3., 6., 9.], dev=dev)}}
    container = Container(dict_in)
    container_mean = container.mean()
    assert np.allclose(ivy.to_numpy(container_mean['a']), np.array([2.]))
    assert np.allclose(ivy.to_numpy(container_mean.a), np.array([2.]))
    assert np.allclose(ivy.to_numpy(container_mean['b']['c']), np.array([4.]))
    assert np.allclose(ivy.to_numpy(container_mean.b.c), np.array([4.]))
    assert np.allclose(ivy.to_numpy(container_mean['b']['d']), np.array([6.]))
    assert np.allclose(ivy.to_numpy(container_mean.b.d), np.array([6.]))


# def test_container_var(dev, call):
#     dict_in = {'a': ivy.array([1., 2., 3.], dev=dev),
#                'b': {'c': ivy.array([2., 4., 6.], dev=dev), 'd': ivy.array([3., 6., 9.], dev=dev)}}
#     container = Container(dict_in)
#     container_var = container.var()
#     assert np.allclose(ivy.to_numpy(container_var['a']), np.array([2 / 3]))
#     assert np.allclose(ivy.to_numpy(container_var.a), np.array([2 / 3]))
#     assert np.allclose(ivy.to_numpy(container_var['b']['c']), np.array([8 / 3]))
#     assert np.allclose(ivy.to_numpy(container_var.b.c), np.array([8 / 3]))
#     assert np.allclose(ivy.to_numpy(container_var['b']['d']), np.array([6.]))
#     assert np.allclose(ivy.to_numpy(container_var.b.d), np.array([6.]))


# def test_container_std(dev, call):
#     dict_in = {'a': ivy.array([1., 2., 3.], dev=dev),
#                'b': {'c': ivy.array([2., 4., 6.], dev=dev), 'd': ivy.array([3., 6., 9.], dev=dev)}}
#     container = Container(dict_in)
#     container_std = container.std()
#     assert np.allclose(ivy.to_numpy(container_std['a']), np.array([2 / 3]) ** 0.5)
#     assert np.allclose(ivy.to_numpy(container_std.a), np.array([2 / 3]) ** 0.5)
#     assert np.allclose(ivy.to_numpy(container_std['b']['c']), np.array([8 / 3]) ** 0.5)
#     assert np.allclose(ivy.to_numpy(container_std.b.c), np.array([8 / 3]) ** 0.5)
#     assert np.allclose(ivy.to_numpy(container_std['b']['d']), np.array([6.]) ** 0.5)
#     assert np.allclose(ivy.to_numpy(container_std.b.d), np.array([6.]) ** 0.5)


def test_container_minimum(dev, call):
    container = Container({'a': ivy.array([1., 2., 3.], dev=dev),
                           'b': {'c': ivy.array([2., 4., 6.], dev=dev),
                                 'd': ivy.array([3., 6., 9.], dev=dev)}})
    other = Container({'a': ivy.array([2., 3., 2.], dev=dev),
                       'b': {'c': ivy.array([1., 5., 4.], dev=dev),
                             'd': ivy.array([4., 7., 8.], dev=dev)}})

    # against number
    container_minimum = container.minimum(5.)
    assert np.allclose(ivy.to_numpy(container_minimum['a']), np.array([1., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_minimum.a), np.array([1., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_minimum['b']['c']), np.array([2., 4., 5.]))
    assert np.allclose(ivy.to_numpy(container_minimum.b.c), np.array([2., 4., 5.]))
    assert np.allclose(ivy.to_numpy(container_minimum['b']['d']), np.array([3., 5., 5.]))
    assert np.allclose(ivy.to_numpy(container_minimum.b.d), np.array([3., 5., 5.]))

    # against container
    container_minimum = container.minimum(other)
    assert np.allclose(ivy.to_numpy(container_minimum['a']), np.array([1., 2., 2.]))
    assert np.allclose(ivy.to_numpy(container_minimum.a), np.array([1., 2., 2.]))
    assert np.allclose(ivy.to_numpy(container_minimum['b']['c']), np.array([1., 4., 4.]))
    assert np.allclose(ivy.to_numpy(container_minimum.b.c), np.array([1., 4., 4.]))
    assert np.allclose(ivy.to_numpy(container_minimum['b']['d']), np.array([3., 6., 8.]))
    assert np.allclose(ivy.to_numpy(container_minimum.b.d), np.array([3., 6., 8.]))


def test_container_maximum(dev, call):
    container = Container({'a': ivy.array([1., 2., 3.], dev=dev),
                           'b': {'c': ivy.array([2., 4., 6.], dev=dev),
                                 'd': ivy.array([3., 6., 9.], dev=dev)}})
    other = Container({'a': ivy.array([2., 3., 2.], dev=dev),
                       'b': {'c': ivy.array([1., 5., 4.], dev=dev),
                             'd': ivy.array([4., 7., 8.], dev=dev)}})

    # against number
    container_maximum = container.maximum(4.)
    assert np.allclose(ivy.to_numpy(container_maximum['a']), np.array([4., 4., 4.]))
    assert np.allclose(ivy.to_numpy(container_maximum.a), np.array([4., 4., 4.]))
    assert np.allclose(ivy.to_numpy(container_maximum['b']['c']), np.array([4., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container_maximum.b.c), np.array([4., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container_maximum['b']['d']), np.array([4., 6., 9.]))
    assert np.allclose(ivy.to_numpy(container_maximum.b.d), np.array([4., 6., 9.]))

    # against container
    container_maximum = container.maximum(other)
    assert np.allclose(ivy.to_numpy(container_maximum['a']), np.array([2., 3., 3.]))
    assert np.allclose(ivy.to_numpy(container_maximum.a), np.array([2., 3., 3.]))
    assert np.allclose(ivy.to_numpy(container_maximum['b']['c']), np.array([2., 5., 6.]))
    assert np.allclose(ivy.to_numpy(container_maximum.b.c), np.array([2., 5., 6.]))
    assert np.allclose(ivy.to_numpy(container_maximum['b']['d']), np.array([4., 7., 9.]))
    assert np.allclose(ivy.to_numpy(container_maximum.b.d), np.array([4., 7., 9.]))


def test_container_clip(dev, call):
    container = Container({'a': ivy.array([1., 2., 3.], dev=dev),
                           'b': {'c': ivy.array([2., 4., 6.], dev=dev),
                                 'd': ivy.array([3., 6., 9.], dev=dev)}})
    container_min = Container({'a': ivy.array([2., 0., 0.], dev=dev),
                               'b': {'c': ivy.array([0., 5., 0.], dev=dev),
                                     'd': ivy.array([4., 7., 0.], dev=dev)}})
    container_max = Container({'a': ivy.array([3., 1., 2.], dev=dev),
                               'b': {'c': ivy.array([1., 7., 5.], dev=dev),
                                     'd': ivy.array([5., 8., 8.], dev=dev)}})

    # against number
    container_clipped = container.clip(2., 6.)
    assert np.allclose(ivy.to_numpy(container_clipped['a']), np.array([2., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_clipped.a), np.array([2., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_clipped['b']['c']), np.array([2., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container_clipped.b.c), np.array([2., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container_clipped['b']['d']), np.array([3., 6., 6.]))
    assert np.allclose(ivy.to_numpy(container_clipped.b.d), np.array([3., 6., 6.]))

    if call is helpers.mx_call:
        # MXNet clip does not support arrays for the min and max arguments
        return

    # against container
    container_clipped = container.clip(container_min, container_max)
    assert np.allclose(ivy.to_numpy(container_clipped['a']), np.array([2., 1., 2.]))
    assert np.allclose(ivy.to_numpy(container_clipped.a), np.array([2., 1., 2.]))
    assert np.allclose(ivy.to_numpy(container_clipped['b']['c']), np.array([1., 5., 5.]))
    assert np.allclose(ivy.to_numpy(container_clipped.b.c), np.array([1., 5., 5.]))
    assert np.allclose(ivy.to_numpy(container_clipped['b']['d']), np.array([4., 7., 8.]))
    assert np.allclose(ivy.to_numpy(container_clipped.b.d), np.array([4., 7., 8.]))


def test_container_clip_vector_norm(dev, call):
    container = Container({'a': ivy.array([[0.8, 2.2], [1.5, 0.2]], dev=dev)})
    container_clipped = container.clip_vector_norm(2.5, 2.)
    assert np.allclose(ivy.to_numpy(container_clipped['a']),
                       np.array([[0.71749604, 1.9731141], [1.345305, 0.17937401]]))
    assert np.allclose(ivy.to_numpy(container_clipped.a),
                       np.array([[0.71749604, 1.9731141], [1.345305, 0.17937401]]))


def test_container_einsum(dev, call):
    dict_in = {'a': ivy.array([[1., 2.], [3., 4.], [5., 6.]], dev=dev),
               'b': {'c': ivy.array([[2., 4.], [6., 8.], [10., 12.]], dev=dev),
                     'd': ivy.array([[-2., -4.], [-6., -8.], [-10., -12.]], dev=dev)}}
    container = Container(dict_in)
    container_einsummed = container.einsum('ij->i')
    assert np.allclose(ivy.to_numpy(container_einsummed['a']), np.array([3., 7., 11.]))
    assert np.allclose(ivy.to_numpy(container_einsummed.a), np.array([3., 7., 11.]))
    assert np.allclose(ivy.to_numpy(container_einsummed['b']['c']), np.array([6., 14., 22.]))
    assert np.allclose(ivy.to_numpy(container_einsummed.b.c), np.array([6., 14., 22.]))
    assert np.allclose(ivy.to_numpy(container_einsummed['b']['d']), np.array([-6., -14., -22.]))
    assert np.allclose(ivy.to_numpy(container_einsummed.b.d), np.array([-6., -14., -22.]))


# def test_container_vector_norm(dev, call):
#     dict_in = {'a': ivy.array([[1., 2.], [3., 4.], [5., 6.]], dev=dev),
#                'b': {'c': ivy.array([[2., 4.], [6., 8.], [10., 12.]], dev=dev),
#                      'd': ivy.array([[3., 6.], [9., 12.], [15., 18.]], dev=dev)}}
#     container = Container(dict_in)
#     container_normed = container.vector_norm(axis=(-1, -2))
#     assert np.allclose(ivy.to_numpy(container_normed['a']), 9.5394)
#     assert np.allclose(ivy.to_numpy(container_normed.a), 9.5394)
#     assert np.allclose(ivy.to_numpy(container_normed['b']['c']), 19.0788)
#     assert np.allclose(ivy.to_numpy(container_normed.b.c), 19.0788)
#     assert np.allclose(ivy.to_numpy(container_normed['b']['d']), 28.6182)
#     assert np.allclose(ivy.to_numpy(container_normed.b.d), 28.6182)


def test_container_matrix_norm(dev, call):
    if call is helpers.mx_call:
        # MXNet does not support matrix norm
        pytest.skip()
    dict_in = {'a': ivy.array([[1., 2.], [3., 4.], [5., 6.]], dev=dev),
               'b': {'c': ivy.array([[2., 4.], [6., 8.], [10., 12.]], dev=dev),
                     'd': ivy.array([[3., 6.], [9., 12.], [15., 18.]], dev=dev)}}
    container = Container(dict_in)
    container_normed = container.matrix_norm()
    assert np.allclose(ivy.to_numpy(container_normed['a']), 9.52551809)
    assert np.allclose(ivy.to_numpy(container_normed.a), 9.52551809)
    assert np.allclose(ivy.to_numpy(container_normed['b']['c']), 19.05103618)
    assert np.allclose(ivy.to_numpy(container_normed.b.c), 19.05103618)
    assert np.allclose(ivy.to_numpy(container_normed['b']['d']), 28.57655427)
    assert np.allclose(ivy.to_numpy(container_normed.b.d), 28.57655427)


def test_container_flip(dev, call):
    dict_in = {'a': ivy.array([[1., 2.], [3., 4.], [5., 6.]], dev=dev),
               'b': {'c': ivy.array([[2., 4.], [6., 8.], [10., 12.]], dev=dev),
                     'd': ivy.array([[-2., -4.], [-6., -8.], [-10., -12.]], dev=dev)}}
    container = Container(dict_in)
    container_flipped = container.flip(-1)
    assert np.allclose(ivy.to_numpy(container_flipped['a']), np.array([[2., 1.], [4., 3.], [6., 5.]]))
    assert np.allclose(ivy.to_numpy(container_flipped.a), np.array([[2., 1.], [4., 3.], [6., 5.]]))
    assert np.allclose(ivy.to_numpy(container_flipped['b']['c']), np.array([[4., 2.], [8., 6.], [12., 10.]]))
    assert np.allclose(ivy.to_numpy(container_flipped.b.c), np.array([[4., 2.], [8., 6.], [12., 10.]]))
    assert np.allclose(ivy.to_numpy(container_flipped['b']['d']), np.array([[-4., -2.], [-8., -6.], [-12., -10.]]))
    assert np.allclose(ivy.to_numpy(container_flipped.b.d), np.array([[-4., -2.], [-8., -6.], [-12., -10.]]))


def test_container_as_ones(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)

    container_ones = container.as_ones()
    assert np.allclose(ivy.to_numpy(container_ones['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_ones.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_ones['b']['c']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_ones.b.c), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_ones['b']['d']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_ones.b.d), np.array([1]))


def test_container_as_zeros(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)

    container_zeros = container.as_zeros()
    assert np.allclose(ivy.to_numpy(container_zeros['a']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container_zeros.a), np.array([0]))
    assert np.allclose(ivy.to_numpy(container_zeros['b']['c']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container_zeros.b.c), np.array([0]))
    assert np.allclose(ivy.to_numpy(container_zeros['b']['d']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container_zeros.b.d), np.array([0]))


def test_container_as_bools(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': [], 'd': True}}
    container = Container(dict_in)

    container_bools = container.as_bools()
    assert container_bools['a'] is True
    assert container_bools.a is True
    assert container_bools['b']['c'] is False
    assert container_bools.b.c is False
    assert container_bools['b']['d'] is True
    assert container_bools.b.d is True


def test_container_all_true(dev, call):
    assert not Container({'a': ivy.array([1], dev=dev), 'b': {'c': [], 'd': True}}).all_true()
    assert Container({'a': ivy.array([1], dev=dev), 'b': {'c': [1], 'd': True}}).all_true()
    # noinspection PyBroadException
    try:
        assert Container({'a': ivy.array([1], dev=dev), 'b': {'c': [1], 'd': True}}).all_true(
            assert_is_bool=True)
        error_raised = False
    except AssertionError:
        error_raised = True
    assert error_raised


def test_container_all_false(dev, call):
    assert Container({'a': False, 'b': {'c': [], 'd': 0}}).all_false()
    assert not Container({'a': False, 'b': {'c': [1], 'd': 0}}).all_false()
    # noinspection PyBroadException
    try:
        assert Container({'a': ivy.array([1], dev=dev), 'b': {'c': [1], 'd': True}}).all_false(
            assert_is_bool=True)
        error_raised = False
    except AssertionError:
        error_raised = True
    assert error_raised


def test_container_as_random_uniform(dev, call):
    dict_in = {'a': ivy.array([1.], dev=dev),
               'b': {'c': ivy.array([2.], dev=dev), 'd': ivy.array([3.], dev=dev)}}
    container = Container(dict_in)

    container_random = container.as_random_uniform()
    assert (ivy.to_numpy(container_random['a']) != np.array([1.]))[0]
    assert (ivy.to_numpy(container_random.a) != np.array([1.]))[0]
    assert (ivy.to_numpy(container_random['b']['c']) != np.array([2.]))[0]
    assert (ivy.to_numpy(container_random.b.c) != np.array([2.]))[0]
    assert (ivy.to_numpy(container_random['b']['d']) != np.array([3.]))[0]
    assert (ivy.to_numpy(container_random.b.d) != np.array([3.]))[0]


def test_container_expand_dims(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_expanded_dims = container.expand_dims(0)
    assert np.allclose(ivy.to_numpy(container_expanded_dims['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.c), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.d), np.array([[3]]))

    # with key_chains to apply
    container_expanded_dims = container.expand_dims(0, ['a', 'b/c'])
    assert np.allclose(ivy.to_numpy(container_expanded_dims['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.c), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.d), np.array([3]))

    # with key_chains to apply pruned
    container_expanded_dims = container.expand_dims(0, ['a', 'b/c'], prune_unapplied=True)
    assert np.allclose(ivy.to_numpy(container_expanded_dims['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.c), np.array([[2]]))
    assert 'b/d' not in container_expanded_dims

    # with key_chains to not apply
    container_expanded_dims = container.expand_dims(0, Container({'a': None, 'b': {'d': None}}), to_apply=False)
    assert np.allclose(ivy.to_numpy(container_expanded_dims['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.c), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.d), np.array([3]))

    # with key_chains to not apply pruned
    container_expanded_dims = container.expand_dims(0, Container({'a': None, 'b': {'d': None}}), to_apply=False,
                                                    prune_unapplied=True)
    assert 'a' not in container_expanded_dims
    assert np.allclose(ivy.to_numpy(container_expanded_dims['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_expanded_dims.b.c), np.array([[2]]))
    assert 'b/d' not in container_expanded_dims


def test_container_clone(dev, call):
    dict_in = {'a': ivy.array([[1], [2], [3]], dev=dev),
               'b': {'c': ivy.array([[2], [3], [4]], dev=dev),
                     'd': ivy.array([[3], [4], [5]], dev=dev)}}
    container = Container(dict_in)

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)

    # without key_chains specification
    container_cloned = container.dev_clone(devs)
    assert isinstance(container_cloned, ivy.DevClonedItem)
    assert min([cont.dev_str == ds for ds, cont in container_cloned.items()])
    assert ivy.Container.multi_map(
        lambda xs, _: ivy.arrays_equal(xs), [c for c in container_cloned.values()]).all_true()


@pytest.mark.parametrize(
    "devs_as_dict", [True, False])
def test_container_distribute(devs_as_dict, dev, call):
    array_a = ivy.array([[1], [2], [3], [4]], dev=dev)
    array_bc = ivy.array([[2], [3], [4], [5]], dev=dev)
    array_bd = ivy.array([[3], [4], [5], [6]], dev=dev)
    dict_in = {'a': array_a, 'b': {'c': array_bc, 'd': array_bd}}
    container = Container(dict_in)
    batch_size = array_a.shape[0]

    if call is helpers.mx_call:
        # MXNet does not support splitting along an axis with a remainder after division.
        pytest.skip()

    # devices
    dev0 = dev
    devs = [dev0]
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)
    if devs_as_dict:
        devs = dict(zip(devs, [int((1/len(devs))*4)]*len(devs)))
    num_devs = len(devs)
    sub_size = int(batch_size/num_devs)

    # without key_chains specification
    container_dist = container.dev_dist(devs)
    assert isinstance(container_dist, ivy.DevDistItem)
    assert min([cont.dev_str == ds for ds, cont in container_dist.items()])
    for i, sub_cont in enumerate(container_dist.values()):
        assert np.array_equal(ivy.to_numpy(sub_cont.a), ivy.to_numpy(array_a)[i*sub_size:i*sub_size+sub_size])
        assert np.array_equal(ivy.to_numpy(sub_cont.b.c), ivy.to_numpy(array_bc)[i*sub_size:i*sub_size+sub_size])
        assert np.array_equal(ivy.to_numpy(sub_cont.b.d), ivy.to_numpy(array_bd)[i*sub_size:i*sub_size+sub_size])


def test_container_unstack(dev, call):
    dict_in = {'a': ivy.array([[1], [2], [3]], dev=dev),
               'b': {'c': ivy.array([[2], [3], [4]], dev=dev),
                     'd': ivy.array([[3], [4], [5]], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_unstacked = container.unstack(0)
    for cont, a, bc, bd in zip(container_unstacked, [1, 2, 3], [2, 3, 4], [3, 4, 5]):
        assert np.array_equal(ivy.to_numpy(cont['a']), np.array([a]))
        assert np.array_equal(ivy.to_numpy(cont.a), np.array([a]))
        assert np.array_equal(ivy.to_numpy(cont['b']['c']), np.array([bc]))
        assert np.array_equal(ivy.to_numpy(cont.b.c), np.array([bc]))
        assert np.array_equal(ivy.to_numpy(cont['b']['d']), np.array([bd]))
        assert np.array_equal(ivy.to_numpy(cont.b.d), np.array([bd]))


def test_container_split(dev, call):
    dict_in = {'a': ivy.array([[1], [2], [3]], dev=dev),
               'b': {'c': ivy.array([[2], [3], [4]], dev=dev),
                     'd': ivy.array([[3], [4], [5]], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_split = container.split(1, -1)
    for cont, a, bc, bd in zip(container_split, [1, 2, 3], [2, 3, 4], [3, 4, 5]):
        assert np.array_equal(ivy.to_numpy(cont['a'])[0], np.array([a]))
        assert np.array_equal(ivy.to_numpy(cont.a)[0], np.array([a]))
        assert np.array_equal(ivy.to_numpy(cont['b']['c'])[0], np.array([bc]))
        assert np.array_equal(ivy.to_numpy(cont.b.c)[0], np.array([bc]))
        assert np.array_equal(ivy.to_numpy(cont['b']['d'])[0], np.array([bd]))
        assert np.array_equal(ivy.to_numpy(cont.b.d)[0], np.array([bd]))


def test_container_gather(dev, call):
    dict_in = {'a': ivy.array([1, 2, 3, 4, 5, 6], dev=dev),
               'b': {'c': ivy.array([2, 3, 4, 5], dev=dev), 'd': ivy.array([10, 9, 8, 7, 6], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_gathered = container.gather(ivy.array([1, 3], dev=dev))
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([9, 7]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([9, 7]))

    # with key_chains to apply
    container_gathered = container.gather(ivy.array([1, 3], dev=dev), -1, ['a', 'b/c'])
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([10, 9, 8, 7, 6]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([10, 9, 8, 7, 6]))

    # with key_chains to apply pruned
    container_gathered = container.gather(ivy.array([1, 3], dev=dev), -1, ['a', 'b/c'], prune_unapplied=True)
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([2, 4]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([3, 5]))
    assert 'b/d' not in container_gathered

    # with key_chains to not apply
    container_gathered = container.gather(ivy.array([1, 3], dev=dev), -1,
                                          Container({'a': None, 'b': {'d': None}}),
                                          to_apply=False)
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([1, 2, 3, 4, 5, 6]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([1, 2, 3, 4, 5, 6]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([10, 9, 8, 7, 6]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([10, 9, 8, 7, 6]))

    # with key_chains to not apply pruned
    container_gathered = container.gather(ivy.array([1, 3], dev=dev), -1,
                                          Container({'a': None, 'b': {'d': None}}),
                                          to_apply=False, prune_unapplied=True)
    assert 'a' not in container_gathered
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([3, 5]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([3, 5]))
    assert 'b/d' not in container_gathered


def test_container_gather_nd(dev, call):
    dict_in = {'a': ivy.array([[[1, 2], [3, 4]],
                               [[5, 6], [7, 8]]], dev=dev),
               'b': {'c': ivy.array([[[8, 7], [6, 5]],
                                     [[4, 3], [2, 1]]], dev=dev),
                     'd': ivy.array([[[2, 4], [6, 8]],
                                     [[10, 12], [14, 16]]], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_gathered = container.gather_nd(ivy.array([[0, 1], [1, 0]], dev=dev))
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([[6, 8], [10, 12]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([[6, 8], [10, 12]]))

    # with key_chains to apply
    container_gathered = container.gather_nd(ivy.array([[0, 1], [1, 0]], dev=dev), ['a', 'b/c'])
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([[[2, 4], [6, 8]],
                                                                             [[10, 12], [14, 16]]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([[[2, 4], [6, 8]],
                                                                       [[10, 12], [14, 16]]]))

    # with key_chains to apply pruned
    container_gathered = container.gather_nd(ivy.array([[0, 1], [1, 0]], dev=dev), ['a', 'b/c'],
                                             prune_unapplied=True)
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([[3, 4], [5, 6]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([[6, 5], [4, 3]]))
    assert 'b/d' not in container_gathered

    # with key_chains to not apply
    container_gathered = container.gather_nd(ivy.array([[0, 1], [1, 0]], dev=dev),
                                             Container({'a': None, 'b': {'d': None}}),
                                             to_apply=False)
    assert np.allclose(ivy.to_numpy(container_gathered['a']), np.array([[[1, 2], [3, 4]],
                                                                        [[5, 6], [7, 8]]]))
    assert np.allclose(ivy.to_numpy(container_gathered.a), np.array([[[1, 2], [3, 4]],
                                                                     [[5, 6], [7, 8]]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered['b']['d']), np.array([[[2, 4], [6, 8]],
                                                                             [[10, 12], [14, 16]]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.d), np.array([[[2, 4], [6, 8]],
                                                                       [[10, 12], [14, 16]]]))

    # with key_chains to not apply pruned
    container_gathered = container.gather_nd(ivy.array([[0, 1], [1, 0]], dev=dev),
                                             Container({'a': None, 'b': {'d': None}}),
                                             to_apply=False, prune_unapplied=True)
    assert 'a' not in container_gathered
    assert np.allclose(ivy.to_numpy(container_gathered['b']['c']), np.array([[6, 5], [4, 3]]))
    assert np.allclose(ivy.to_numpy(container_gathered.b.c), np.array([[6, 5], [4, 3]]))
    assert 'b/d' not in container_gathered


def test_container_repeat(dev, call):
    if call is helpers.mx_call:
        # MXNet does not support repeats specified as array
        pytest.skip()
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_repeated = container.repeat(ivy.array([2, 1, 0, 3], dev=dev), -1)
    assert np.allclose(ivy.to_numpy(container_repeated['a']), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.a), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['d']), np.array([[10., 10., 9., 7., 7., 7.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.d), np.array([[10., 10., 9., 7., 7., 7.]]))

    # with key_chains to apply
    container_repeated = container.repeat(ivy.array([2, 1, 0, 3], dev=dev), -1, ['a', 'b/c'])
    assert np.allclose(ivy.to_numpy(container_repeated['a']), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.a), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['d']), np.array([[10., 9., 8., 7.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.d), np.array([[10., 9., 8., 7.]]))

    # with key_chains to apply pruned
    container_repeated = container.repeat(ivy.array([2, 1, 0, 3], dev=dev), -1, ['a', 'b/c'],
                                          prune_unapplied=True)
    assert np.allclose(ivy.to_numpy(container_repeated['a']), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.a), np.array([[0., 0., 1., 3., 3., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert 'b/d' not in container_repeated

    # with key_chains to not apply
    container_repeated = container.repeat(ivy.array([2, 1, 0, 3], dev=dev), -1,
                                          Container({'a': None, 'b': {'d': None}}),
                                          to_apply=False)
    assert np.allclose(ivy.to_numpy(container_repeated['a']), np.array([[0., 1., 2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.a), np.array([[0., 1., 2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['d']), np.array([[10., 9., 8., 7.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.d), np.array([[10., 9., 8., 7.]]))

    # with key_chains to not apply pruned
    container_repeated = container.repeat(ivy.array([2, 1, 0, 3], dev=dev), -1,
                                          Container({'a': None, 'b': {'d': None}}),
                                          to_apply=False, prune_unapplied=True)
    assert 'a' not in container_repeated
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c), np.array([[5., 5., 10., 20., 20., 20.]]))
    assert 'b/d' not in container_repeated


def test_container_swapaxes(dev, call):
    if call is helpers.mx_call:
        # MXNet does not support repeats specified as array
        pytest.skip()
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_swapped = container.swapaxes(0, 1)
    assert np.allclose(ivy.to_numpy(container_swapped['a']), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.a), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['d']), np.array([[10.], [9.], [8.], [7.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.d), np.array([[10.], [9.], [8.], [7.]]))

    # with key_chains to apply
    container_swapped = container.swapaxes(0, 1, ['a', 'b/c'])
    assert np.allclose(ivy.to_numpy(container_swapped['a']), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.a), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['d']), np.array([10., 9., 8., 7.]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.d), np.array([10., 9., 8., 7.]))

    # with key_chains to apply pruned
    container_swapped = container.swapaxes(0, 1, ['a', 'b/c'], prune_unapplied=True)
    assert np.allclose(ivy.to_numpy(container_swapped['a']), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.a), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert 'b/d' not in container_swapped

    # with key_chains to not apply
    container_swapped = container.swapaxes(0, 1, Container({'a': None, 'b': {'d': None}}), to_apply=False)
    assert np.allclose(ivy.to_numpy(container_swapped['a']), np.array([0., 1., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_swapped.a), np.array([0., 1., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped['b']['d']), np.array([10., 9., 8., 7.]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.d), np.array([10., 9., 8., 7.]))

    # with key_chains to not apply pruned
    container_swapped = container.swapaxes(0, 1, Container({'a': None, 'b': {'d': None}}), to_apply=False,
                                           prune_unapplied=True)
    assert 'a' not in container_swapped
    assert np.allclose(ivy.to_numpy(container_swapped['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_swapped.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert 'b/d' not in container_swapped


def test_container_reshape(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    # pre_shape only
    container_reshaped = container.reshape((1, 2, 2))
    assert np.allclose(ivy.to_numpy(container_reshaped['a']), np.array([[0., 1.], [2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.a), np.array([[0., 1.], [2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['c']), np.array([[5., 10.], [15., 20.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.c), np.array([[5., 10.], [15., 20.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['d']), np.array([[10., 9.], [8., 7.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.d), np.array([[10., 9.], [8., 7.]]))

    # pre_shape and slice
    dict_in = {'a': ivy.array([[[0., 1., 2., 3.], [0., 1., 2., 3.]]], dev=dev),
               'b': {'c': ivy.array([[[5., 10., 15.], [20., 25., 30.]]], dev=dev),
                     'd': ivy.array([[[10.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    container_reshaped = container.reshape((-1,), slice(2, None))
    assert np.allclose(ivy.to_numpy(container_reshaped['a']), np.array([[0., 1., 2., 3.], [0., 1., 2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.a), np.array([[0., 1., 2., 3.], [0., 1., 2., 3.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['c']), np.array([[5., 10., 15.], [20., 25., 30.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.c), np.array([[5., 10., 15.], [20., 25., 30.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['d']), np.array([[10.], [9.]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.d), np.array([[10.], [9.]]))

    # pre_shape, slice and post_shape
    dict_in = {'a': ivy.array([[[0., 1., 2., 3.], [0., 1., 2., 3.]]], dev=dev),
               'b': {'c': ivy.array([[[5., 10., 15.], [20., 25., 30.]]], dev=dev),
                     'd': ivy.array([[[10.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    container_reshaped = container.reshape((-1,), slice(2, None), (1,))
    assert np.allclose(ivy.to_numpy(container_reshaped['a']), np.array([[[0.], [1.], [2.], [3.]],
                                                                        [[0.], [1.], [2.], [3.]]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.a), np.array([[[0.], [1.], [2.], [3.]],
                                                                     [[0.], [1.], [2.], [3.]]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['c']), np.array([[[5.], [10.], [15.]],
                                                                             [[20.], [25.], [30.]]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.c), np.array([[[5.], [10.], [15.]],
                                                                       [[20.], [25.], [30.]]]))
    assert np.allclose(ivy.to_numpy(container_reshaped['b']['d']), np.array([[[10.]], [[9.]]]))
    assert np.allclose(ivy.to_numpy(container_reshaped.b.d), np.array([[[10.]], [[9.]]]))


def test_container_einops_rearrange(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    container_rearranged = container.einops_rearrange('b n -> n b')
    assert np.allclose(ivy.to_numpy(container_rearranged['a']), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_rearranged.a), np.array([[0.], [1.], [2.], [3.]]))
    assert np.allclose(ivy.to_numpy(container_rearranged['b']['c']), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_rearranged.b.c), np.array([[5.], [10.], [15.], [20.]]))
    assert np.allclose(ivy.to_numpy(container_rearranged['b']['d']), np.array([[10.], [9.], [8.], [7.]]))
    assert np.allclose(ivy.to_numpy(container_rearranged.b.d), np.array([[10.], [9.], [8.], [7.]]))


def test_container_einops_reduce(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    container_reduced = container.einops_reduce('b n -> b', 'mean')
    assert np.allclose(ivy.to_numpy(container_reduced['a']), np.array([1.5]))
    assert np.allclose(ivy.to_numpy(container_reduced.a), np.array([1.5]))
    assert np.allclose(ivy.to_numpy(container_reduced['b']['c']), np.array([12.5]))
    assert np.allclose(ivy.to_numpy(container_reduced.b.c), np.array([12.5]))
    assert np.allclose(ivy.to_numpy(container_reduced['b']['d']), np.array([8.5]))
    assert np.allclose(ivy.to_numpy(container_reduced.b.d), np.array([8.5]))


def test_container_einops_repeat(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    container_repeated = container.einops_repeat('b n -> b n c', c=2)
    assert np.allclose(ivy.to_numpy(container_repeated['a']),
                       np.array([[[0., 0.], [1., 1.], [2., 2.], [3., 3.]]]))
    assert np.allclose(ivy.to_numpy(container_repeated.a),
                       np.array([[[0., 0.], [1., 1.], [2., 2.], [3., 3.]]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['c']),
                       np.array([[[5., 5.], [10., 10.], [15., 15.], [20., 20.]]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.c),
                       np.array([[[5., 5.], [10., 10.], [15., 15.], [20., 20.]]]))
    assert np.allclose(ivy.to_numpy(container_repeated['b']['d']),
                       np.array([[[10., 10.], [9., 9.], [8., 8.], [7., 7.]]]))
    assert np.allclose(ivy.to_numpy(container_repeated.b.d),
                       np.array([[[10., 10.], [9., 9.], [8., 8.], [7., 7.]]]))


def test_container_to_dev(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)

    container_to_cpu = container.to_dev(dev)
    assert ivy.dev(container_to_cpu['a'], as_str=True) == dev
    assert ivy.dev(container_to_cpu.a, as_str=True) == dev
    assert ivy.dev(container_to_cpu['b']['c'], as_str=True) == dev
    assert ivy.dev(container_to_cpu.b.c, as_str=True) == dev
    assert ivy.dev(container_to_cpu['b']['d'], as_str=True) == dev
    assert ivy.dev(container_to_cpu.b.d, as_str=True) == dev


def test_container_stop_gradients(dev, call):
    dict_in = {'a': ivy.variable(ivy.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], dev=dev)),
               'b': {'c': ivy.variable(ivy.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]], dev=dev)),
                     'd': ivy.variable(ivy.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]], dev=dev))}}
    container = Container(dict_in)
    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(container['a'])
        assert ivy.is_variable(container.a)
        assert ivy.is_variable(container['b']['c'])
        assert ivy.is_variable(container.b.c)
        assert ivy.is_variable(container['b']['d'])
        assert ivy.is_variable(container.b.d)

    # without key_chains specification
    container_stopped_grads = container.stop_gradients()
    assert ivy.is_native_array(container_stopped_grads['a'])
    assert ivy.is_native_array(container_stopped_grads.a)
    assert ivy.is_native_array(container_stopped_grads['b']['c'])
    assert ivy.is_native_array(container_stopped_grads.b.c)
    assert ivy.is_native_array(container_stopped_grads['b']['d'])
    assert ivy.is_native_array(container_stopped_grads.b.d)

    # with key_chains to apply
    container_stopped_grads = container.stop_gradients(key_chains=['a', 'b/c'])
    assert ivy.is_native_array(container_stopped_grads['a'])
    assert ivy.is_native_array(container_stopped_grads.a)
    assert ivy.is_native_array(container_stopped_grads['b']['c'])
    assert ivy.is_native_array(container_stopped_grads.b.c)
    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(container_stopped_grads['b']['d'])
        assert ivy.is_variable(container_stopped_grads.b.d)

    # with key_chains to apply pruned
    container_stopped_grads = container.stop_gradients(key_chains=['a', 'b/c'], prune_unapplied=True)
    assert ivy.is_native_array(container_stopped_grads['a'])
    assert ivy.is_native_array(container_stopped_grads.a)
    assert ivy.is_native_array(container_stopped_grads['b']['c'])
    assert ivy.is_native_array(container_stopped_grads.b.c)
    assert 'b/d' not in container_stopped_grads

    # with key_chains to not apply
    container_stopped_grads = container.stop_gradients(key_chains=Container({'a': None, 'b': {'d': None}}),
                                                       to_apply=False)
    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(container_stopped_grads['a'])
        assert ivy.is_variable(container_stopped_grads.a)
    assert ivy.is_native_array(container_stopped_grads['b']['c'])
    assert ivy.is_native_array(container_stopped_grads.b.c)
    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(container_stopped_grads['b']['d'])
        assert ivy.is_variable(container_stopped_grads.b.d)

    # with key_chains to not apply pruned
    container_stopped_grads = container.stop_gradients(key_chains=Container({'a': None, 'b': {'d': None}}),
                                                       to_apply=False, prune_unapplied=True)
    assert 'a' not in container_stopped_grads
    assert ivy.is_native_array(container_stopped_grads['b']['c'])
    assert ivy.is_native_array(container_stopped_grads.b.c)
    assert 'b/d' not in container_stopped_grads


def test_container_as_variables(dev, call):
    dict_in = {'a': ivy.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], dev=dev),
               'b': {'c': ivy.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]], dev=dev),
                     'd': ivy.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]], dev=dev)}}
    container = Container(dict_in)

    assert ivy.is_native_array(container['a'])
    assert ivy.is_native_array(container.a)
    assert ivy.is_native_array(container['b']['c'])
    assert ivy.is_native_array(container.b.c)
    assert ivy.is_native_array(container['b']['d'])
    assert ivy.is_native_array(container.b.d)

    variable_cont = container.as_variables()

    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(variable_cont['a'])
        assert ivy.is_variable(variable_cont.a)
        assert ivy.is_variable(variable_cont['b']['c'])
        assert ivy.is_variable(variable_cont.b.c)
        assert ivy.is_variable(variable_cont['b']['d'])
        assert ivy.is_variable(variable_cont.b.d)


def test_container_as_arrays(dev, call):
    dict_in = {'a': ivy.variable(ivy.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], dev=dev)),
               'b': {'c': ivy.variable(ivy.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]], dev=dev)),
                     'd': ivy.variable(ivy.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]], dev=dev))}}
    container = Container(dict_in)
    if call is not helpers.np_call:
        # Numpy does not support variables or gradients
        assert ivy.is_variable(container['a'])
        assert ivy.is_variable(container.a)
        assert ivy.is_variable(container['b']['c'])
        assert ivy.is_variable(container.b.c)
        assert ivy.is_variable(container['b']['d'])
        assert ivy.is_variable(container.b.d)

    # without key_chains specification
    container_as_arrays = container.as_arrays()
    assert ivy.is_native_array(container_as_arrays['a'])
    assert ivy.is_native_array(container_as_arrays.a)
    assert ivy.is_native_array(container_as_arrays['b']['c'])
    assert ivy.is_native_array(container_as_arrays.b.c)
    assert ivy.is_native_array(container_as_arrays['b']['d'])
    assert ivy.is_native_array(container_as_arrays.b.d)


def test_container_num_arrays(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10., 15., 20.]], dev=dev),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)
    assert container.num_arrays() == 3
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.variable(ivy.array([[5., 10., 15., 20.]], dev=dev)),
                     'd': ivy.array([[10., 9., 8., 7.]], dev=dev)}}
    container = Container(dict_in)
    assert container.num_arrays() == 3 if call in [helpers.np_call, helpers.jnp_call] else 2


def test_container_size_ordered_arrays(dev, call):
    dict_in = {'a': ivy.array([[0., 1., 2., 3.]], dev=dev),
               'b': {'c': ivy.array([[5., 10.]], dev=dev),
                     'd': ivy.array([[10., 9., 8.]], dev=dev)}}
    container = Container(dict_in)
    size_ordered = container.size_ordered_arrays()
    assert np.allclose(ivy.to_numpy(size_ordered.a), np.array([[0., 1., 2., 3.]]))
    assert np.allclose(ivy.to_numpy(size_ordered.b__c), np.array([[5., 10.]]))
    assert np.allclose(ivy.to_numpy(size_ordered.b__d), np.array([[10., 9., 8.]]))
    for v, arr in zip(size_ordered.values(), [np.array([[5., 10.]]),
                                              np.array([[10., 9., 8.]]),
                                              np.array([[0., 1., 2., 3.]])]):
        assert np.allclose(ivy.to_numpy(v), arr)


def test_container_to_numpy(dev, call):
    dict_in = {'a': ivy.variable(ivy.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], dev=dev)),
               'b': {'c': ivy.variable(ivy.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]], dev=dev)),
                     'd': ivy.variable(ivy.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]], dev=dev))}}
    container = Container(dict_in)

    # before conversion
    assert ivy.is_native_array(container['a'])
    assert ivy.is_native_array(container.a)
    assert ivy.is_native_array(container['b']['c'])
    assert ivy.is_native_array(container.b.c)
    assert ivy.is_native_array(container['b']['d'])
    assert ivy.is_native_array(container.b.d)

    # after conversion
    container_to_numpy = container.to_numpy()
    assert isinstance(container_to_numpy['a'], np.ndarray)
    assert isinstance(container_to_numpy.a, np.ndarray)
    assert isinstance(container_to_numpy['b']['c'], np.ndarray)
    assert isinstance(container_to_numpy.b.c, np.ndarray)
    assert isinstance(container_to_numpy['b']['d'], np.ndarray)
    assert isinstance(container_to_numpy.b.d, np.ndarray)


def test_container_from_numpy(dev, call):
    dict_in = {'a': np.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]]),
               'b': {'c': np.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]]),
                     'd': np.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]])}}

    # before conversion
    container = Container(dict_in)
    assert isinstance(container['a'], np.ndarray)
    assert isinstance(container.a, np.ndarray)
    assert isinstance(container['b']['c'], np.ndarray)
    assert isinstance(container.b.c, np.ndarray)
    assert isinstance(container['b']['d'], np.ndarray)
    assert isinstance(container.b.d, np.ndarray)

    # after conversion
    container_from_numpy = container.from_numpy()
    assert ivy.is_native_array(container_from_numpy['a'])
    assert ivy.is_native_array(container_from_numpy.a)
    assert ivy.is_native_array(container_from_numpy['b']['c'])
    assert ivy.is_native_array(container_from_numpy.b.c)
    assert ivy.is_native_array(container_from_numpy['b']['d'])
    assert ivy.is_native_array(container_from_numpy.b.d)


def test_container_arrays_as_lists(dev, call):
    dict_in = {'a': ivy.array([[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]], dev=dev),
               'b': {'c': ivy.array([[[8., 7.], [6., 5.]], [[4., 3.], [2., 1.]]], dev=dev),
                     'd': ivy.array([[[2., 4.], [6., 8.]], [[10., 12.], [14., 16.]]], dev=dev)}}
    container = Container(dict_in)

    assert ivy.is_native_array(container['a'])
    assert ivy.is_native_array(container.a)
    assert ivy.is_native_array(container['b']['c'])
    assert ivy.is_native_array(container.b.c)
    assert ivy.is_native_array(container['b']['d'])
    assert ivy.is_native_array(container.b.d)

    # without key_chains specification
    container_arrays_as_lists = container.arrays_as_lists()
    assert isinstance(container_arrays_as_lists['a'], list)
    assert isinstance(container_arrays_as_lists.a, list)
    assert isinstance(container_arrays_as_lists['b']['c'], list)
    assert isinstance(container_arrays_as_lists.b.c, list)
    assert isinstance(container_arrays_as_lists['b']['d'], list)
    assert isinstance(container_arrays_as_lists.b.d, list)


def test_container_has_key(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    assert container.has_key('a')
    assert container.has_key('b')
    assert container.has_key('c')
    assert container.has_key('d')
    assert not container.has_key('e')
    assert not container.has_key('f')


def test_container_has_key_chain(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    assert container.has_key_chain('a')
    assert container.has_key_chain('b')
    assert container.has_key_chain('b/c')
    assert container.has_key_chain('b/d')
    assert not container.has_key_chain('b/e')
    assert not container.has_key_chain('c')


def test_container_has_nans(dev, call):
    container = Container({'a': ivy.array([1., 2.], dev=dev),
                           'b': {'c': ivy.array([2., 3.], dev=dev), 'd': ivy.array([3., 4.], dev=dev)}})
    container_nan = Container({'a': ivy.array([1., 2.], dev=dev),
                               'b': {'c': ivy.array([float('nan'), 3.], dev=dev),
                                     'd': ivy.array([3., 4.], dev=dev)}})
    container_inf = Container({'a': ivy.array([1., 2.], dev=dev),
                               'b': {'c': ivy.array([2., 3.], dev=dev),
                                     'd': ivy.array([3., float('inf')], dev=dev)}})
    container_nan_n_inf = Container({'a': ivy.array([1., 2.], dev=dev),
                                     'b': {'c': ivy.array([float('nan'), 3.], dev=dev),
                                           'd': ivy.array([3., float('inf')], dev=dev)}})

    # global

    # with inf check
    assert not container.has_nans()
    assert container_nan.has_nans()
    assert container_inf.has_nans()
    assert container_nan_n_inf.has_nans()

    # without inf check
    assert not container.has_nans(include_infs=False)
    assert container_nan.has_nans(include_infs=False)
    assert not container_inf.has_nans(include_infs=False)
    assert container_nan_n_inf.has_nans(include_infs=False)

    # leafwise

    # with inf check
    container_hn = container.has_nans(leafwise=True)
    assert container_hn.a is False
    assert container_hn.b.c is False
    assert container_hn.b.d is False

    container_nan_hn = container_nan.has_nans(leafwise=True)
    assert container_nan_hn.a is False
    assert container_nan_hn.b.c is True
    assert container_nan_hn.b.d is False

    container_inf_hn = container_inf.has_nans(leafwise=True)
    assert container_inf_hn.a is False
    assert container_inf_hn.b.c is False
    assert container_inf_hn.b.d is True

    container_nan_n_inf_hn = container_nan_n_inf.has_nans(leafwise=True)
    assert container_nan_n_inf_hn.a is False
    assert container_nan_n_inf_hn.b.c is True
    assert container_nan_n_inf_hn.b.d is True

    # without inf check
    container_hn = container.has_nans(leafwise=True, include_infs=False)
    assert container_hn.a is False
    assert container_hn.b.c is False
    assert container_hn.b.d is False

    container_nan_hn = container_nan.has_nans(leafwise=True, include_infs=False)
    assert container_nan_hn.a is False
    assert container_nan_hn.b.c is True
    assert container_nan_hn.b.d is False

    container_inf_hn = container_inf.has_nans(leafwise=True, include_infs=False)
    assert container_inf_hn.a is False
    assert container_inf_hn.b.c is False
    assert container_inf_hn.b.d is False

    container_nan_n_inf_hn = container_nan_n_inf.has_nans(leafwise=True, include_infs=False)
    assert container_nan_n_inf_hn.a is False
    assert container_nan_n_inf_hn.b.c is True
    assert container_nan_n_inf_hn.b.d is False


def test_container_at_keys(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    new_container = container.at_keys(['a', 'c'])
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert 'd' not in new_container['b']
    new_container = container.at_keys('c')
    assert 'a' not in new_container
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert 'd' not in new_container['b']
    new_container = container.at_keys(['b'])
    assert 'a' not in new_container
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([3]))


def test_container_at_key_chain(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)

    # explicit function call
    sub_container = container.at_key_chain('b')
    assert np.allclose(ivy.to_numpy(sub_container['c']), np.array([2]))
    sub_container = container.at_key_chain('b/c')
    assert np.allclose(ivy.to_numpy(sub_container), np.array([2]))

    # overridden built-in function call
    sub_container = container['b']
    assert np.allclose(ivy.to_numpy(sub_container['c']), np.array([2]))
    sub_container = container['b/c']
    assert np.allclose(ivy.to_numpy(sub_container), np.array([2]))


def test_container_at_key_chains(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    target_cont = Container({'a': True, 'b': {'c': True}})
    new_container = container.at_key_chains(target_cont)
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert 'd' not in new_container['b']
    new_container = container.at_key_chains(['b/c', 'b/d'])
    assert 'a' not in new_container
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([3]))
    new_container = container.at_key_chains('b/c')
    assert 'a' not in new_container
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert 'd' not in new_container['b']


@pytest.mark.parametrize(
    "include_empty", [True, False])
def test_container_all_key_chains(include_empty, dev, call):
    a_val = Container() if include_empty else ivy.array([1], dev=dev)
    bc_val = Container() if include_empty else ivy.array([2], dev=dev)
    bd_val = Container() if include_empty else ivy.array([3], dev=dev)
    dict_in = {'a': a_val, 'b': {'c': bc_val, 'd': bd_val}}
    container = Container(dict_in)
    kcs = container.all_key_chains(include_empty)
    assert kcs[0] == 'a'
    assert kcs[1] == 'b/c'
    assert kcs[2] == 'b/d'


@pytest.mark.parametrize(
    "include_empty", [True, False])
def test_container_key_chains_containing(include_empty, dev, call):
    a_val = Container() if include_empty else ivy.array([1], dev=dev)
    bc_val = Container() if include_empty else ivy.array([2], dev=dev)
    bd_val = Container() if include_empty else ivy.array([3], dev=dev)
    dict_in = {'a_sub': a_val, 'b': {'c': bc_val, 'd_sub': bd_val}}
    container = Container(dict_in)
    kcs = container.key_chains_containing('sub', include_empty)
    assert kcs[0] == 'a_sub'
    assert kcs[1] == 'b/d_sub'


# noinspection PyUnresolvedReferences
def test_container_set_at_keys(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container_orig = Container(dict_in)

    # explicit function call
    orig_container = container_orig.copy()
    container = orig_container.set_at_keys({'b': ivy.array([4], dev=dev)})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']), np.array([4]))
    assert not container.has_key('c')
    assert not container.has_key('d')
    container = orig_container.set_at_keys({'a': ivy.array([5], dev=dev), 'c': ivy.array([6], dev=dev)})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([5]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))


# noinspection PyUnresolvedReferences
def test_container_set_at_key_chain(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container_orig = Container(dict_in)

    # explicit function call
    container = container_orig.copy()
    container = container.set_at_key_chain('b/e', ivy.array([4], dev=dev))
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['e']), np.array([4]))
    container = container.set_at_key_chain('f', ivy.array([5], dev=dev))
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['e']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['f']), np.array([5]))

    # overridden built-in function call
    container = container_orig.copy()
    assert 'b/e' not in container
    container['b/e'] = ivy.array([4], dev=dev)
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['e']), np.array([4]))
    assert 'f' not in container
    container['f'] = ivy.array([5], dev=dev)
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['e']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['f']), np.array([5]))


# noinspection PyUnresolvedReferences
def test_container_overwrite_at_key_chain(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container_orig = Container(dict_in)

    # explicit function call
    container = container_orig.copy()
    # noinspection PyBroadException
    try:
        container.overwrite_at_key_chain('b/e', ivy.array([4], dev=dev))
        exception_raised = False
    except Exception:
        exception_raised = True
    assert exception_raised
    container = container.overwrite_at_key_chain('b/d', ivy.array([4], dev=dev))
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([4]))


def test_container_set_at_key_chains(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    target_container = Container({'a': ivy.array([4], dev=dev),
                                  'b': {'d': ivy.array([5], dev=dev)}})
    new_container = container.set_at_key_chains(target_container, inplace=False)
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([4]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([5]))
    target_container = Container({'b': {'c': ivy.array([7], dev=dev)}})
    new_container = container.set_at_key_chains(target_container, inplace=False)
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([7]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([3]))


def test_container_overwrite_at_key_chains(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    target_container = Container({'a': ivy.array([4], dev=dev),
                                  'b': {'d': ivy.array([5], dev=dev)}})
    new_container = container.overwrite_at_key_chains(target_container, inplace=False)
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([4]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([5]))
    target_container = Container({'b': {'c': ivy.array([7], dev=dev)}})
    new_container = container.overwrite_at_key_chains(target_container, inplace=False)
    assert np.allclose(ivy.to_numpy(new_container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(new_container['b']['c']), np.array([7]))
    assert np.allclose(ivy.to_numpy(new_container['b']['d']), np.array([3]))
    # noinspection PyBroadException
    try:
        container.overwrite_at_key_chains(Container({'b': {'e': ivy.array([5], dev=dev)}}))
        exception_raised = False
    except Exception:
        exception_raised = True
    assert exception_raised


def test_container_prune_keys(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    container_pruned = container.prune_keys(['a', 'c'])
    assert 'a' not in container_pruned
    assert np.allclose(ivy.to_numpy(container_pruned['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.b.d), np.array([[3]]))
    assert 'c' not in container_pruned['b']

    def _test_a_exception(container_in):
        try:
            _ = container_in.a
            return False
        except AttributeError:
            return True

    def _test_bc_exception(container_in):
        try:
            _ = container_in.b.c
            return False
        except AttributeError:
            return True

    def _test_bd_exception(container_in):
        try:
            _ = container_in.b.d
            return False
        except AttributeError:
            return True

    assert _test_a_exception(container_pruned)
    assert _test_bc_exception(container_pruned)

    container_pruned = container.prune_keys(['a', 'd'])
    assert 'a' not in container_pruned
    assert np.allclose(ivy.to_numpy(container_pruned['b']['c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned.b.c), np.array([[2]]))
    assert 'd' not in container_pruned['b']
    assert _test_a_exception(container_pruned)
    assert _test_bd_exception(container_pruned)


def test_container_prune_key_chain(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': None}}
    container = Container(dict_in)
    container_pruned = container.prune_key_chain('b/c')
    assert np.allclose(ivy.to_numpy(container_pruned['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.a), np.array([[1]]))
    assert (container_pruned['b']['d'] is None)
    assert (container_pruned.b.d is None)
    assert ('c' not in container_pruned['b'].keys())

    def _test_exception(container_in):
        try:
            _ = container_in.b.c
            return False
        except AttributeError:
            return True

    assert _test_exception(container_pruned)

    container_pruned = container.prune_key_chain('b')
    assert np.allclose(ivy.to_numpy(container_pruned['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.a), np.array([[1]]))
    assert ('b' not in container_pruned.keys())

    def _test_exception(container_in):
        try:
            _ = container_in.b
            return False
        except AttributeError:
            return True

    assert _test_exception(container_pruned)


def test_container_prune_key_chains(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    container_pruned = container.prune_key_chains(['a', 'b/c'])
    assert 'a' not in container_pruned
    assert np.allclose(ivy.to_numpy(container_pruned['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.b.d), np.array([[3]]))
    assert 'c' not in container_pruned['b']

    def _test_a_exception(container_in):
        try:
            _ = container_in.a
            return False
        except AttributeError:
            return True

    def _test_bc_exception(container_in):
        try:
            _ = container_in.b.c
            return False
        except AttributeError:
            return True

    assert _test_a_exception(container_pruned)
    assert _test_bc_exception(container_pruned)

    container_pruned = container.prune_key_chains(Container({'a': True, 'b': {'c': True}}))
    assert 'a' not in container_pruned
    assert np.allclose(ivy.to_numpy(container_pruned['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.b.d), np.array([[3]]))
    assert 'c' not in container_pruned['b']
    assert _test_a_exception(container_pruned)
    assert _test_bc_exception(container_pruned)


def test_container_format_key_chains(dev, call):
    dict_in = {'_a': ivy.array([1], dev=dev),
               'b ': {'c': ivy.array([2], dev=dev), 'd-': ivy.array([3], dev=dev)}}
    cont = Container(dict_in)
    cont_formatted = cont.format_key_chains(lambda s: s.replace('_', '').replace(' ', '').replace('-', ''))
    assert np.allclose(ivy.to_numpy(cont_formatted['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(cont_formatted.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(cont_formatted['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(cont_formatted.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(cont_formatted['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(cont_formatted.b.d), np.array([3]))


def test_container_sort_by_key(dev, call):
    dict_in = {'b': ivy.array([1], dev=dev),
               'a': {'d': ivy.array([2], dev=dev), 'c': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    container_sorted = container.sort_by_key()
    for k, k_true in zip(container_sorted.keys(), ['a', 'b']):
        assert k == k_true
    for k, k_true in zip(container_sorted.a.keys(), ['c', 'd']):
        assert k == k_true


def test_container_prune_empty(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': {}, 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    container_pruned = container.prune_empty()
    assert np.allclose(ivy.to_numpy(container_pruned['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.b.d), np.array([[3]]))
    assert ('c' not in container_pruned['b'])

    def _test_exception(container_in):
        try:
            _ = container_in.b.c
            return False
        except AttributeError:
            return True

    assert _test_exception(container_pruned)


def test_container_prune_key_from_key_chains(dev, call):
    container = Container({'Ayy': ivy.array([1], dev=dev),
                           'Bee': {'Cee': ivy.array([2], dev=dev), 'Dee': ivy.array([3], dev=dev)},
                           'Beh': {'Ceh': ivy.array([4], dev=dev), 'Deh': ivy.array([5], dev=dev)}})

    # absolute
    container_pruned = container.prune_key_from_key_chains('Bee')
    assert np.allclose(ivy.to_numpy(container_pruned['Ayy']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Ayy), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Cee']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Cee), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Dee']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Dee), np.array([[3]]))
    assert ('Bee' not in container_pruned)

    # containing
    container_pruned = container.prune_key_from_key_chains(containing='B')
    assert np.allclose(ivy.to_numpy(container_pruned['Ayy']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Ayy), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Cee']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Cee), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Dee']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Dee), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Ceh']), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Ceh), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Deh']), np.array([[5]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Deh), np.array([[5]]))
    assert ('Bee' not in container_pruned)
    assert ('Beh' not in container_pruned)


def test_container_prune_keys_from_key_chains(dev, call):
    container = Container({'Ayy': ivy.array([1], dev=dev),
                           'Bee': {'Cee': ivy.array([2], dev=dev), 'Dee': ivy.array([3], dev=dev)},
                           'Eee': {'Fff': ivy.array([4], dev=dev)}})

    # absolute
    container_pruned = container.prune_keys_from_key_chains(['Bee', 'Eee'])
    assert np.allclose(ivy.to_numpy(container_pruned['Ayy']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Ayy), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Cee']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Cee), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Dee']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Dee), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Fff']), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Fff), np.array([[4]]))
    assert ('Bee' not in container_pruned)
    assert ('Eee' not in container_pruned)

    # containing
    container_pruned = container.prune_keys_from_key_chains(containing=['B', 'E'])
    assert np.allclose(ivy.to_numpy(container_pruned['Ayy']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Ayy), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Cee']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Cee), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Dee']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Dee), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_pruned['Fff']), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_pruned.Fff), np.array([[4]]))
    assert ('Bee' not in container_pruned)
    assert ('Eee' not in container_pruned)


def test_container_restructure_key_chains(dev, call):

    # single
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_restructured = container.restructure_key_chains({'a': 'A'})
    assert np.allclose(ivy.to_numpy(container_restructured['A']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_restructured.A), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_restructured['b/c']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_restructured.b.c), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_restructured['b/d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_restructured.b.d), np.array([[3]]))

    # full
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_restructured = container.restructure_key_chains({'a': 'A', 'b/c': 'B/C', 'b/d': 'B/D'})
    assert np.allclose(ivy.to_numpy(container_restructured['A']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_restructured.A), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_restructured['B/C']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_restructured.B.C), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_restructured['B/D']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_restructured.B.D), np.array([[3]]))


def test_container_restructure(dev, call):
    container = Container({'a': ivy.array([[1, 2], [3, 4]], dev=dev),
                           'b': {'c': ivy.array([[2, 4], [6, 8]], dev=dev),
                                 'd': ivy.array([3, 6, 9, 12], dev=dev)}})
    container_restructured = container.restructure({'a': {'key_chain': 'A', 'pattern': 'a b -> b a'},
                                                    'b/c': {'key_chain': 'B/C', 'pattern': 'a b -> (a b)'},
                                                    'b/d': {'key_chain': 'B/D', 'pattern': '(a b) -> a b',
                                                            'axes_lengths': {'a': 2, 'b': 2}}}, keep_orig=False)
    assert np.allclose(ivy.to_numpy(container_restructured['A']), np.array([[1, 3], [2, 4]]))
    assert np.allclose(ivy.to_numpy(container_restructured.A), np.array([[1, 3], [2, 4]]))
    assert np.allclose(ivy.to_numpy(container_restructured['B/C']), np.array([2, 4, 6, 8]))
    assert np.allclose(ivy.to_numpy(container_restructured.B.C), np.array([2, 4, 6, 8]))
    assert np.allclose(ivy.to_numpy(container_restructured['B/D']), np.array([[ 3,  6], [ 9, 12]]))
    assert np.allclose(ivy.to_numpy(container_restructured.B.D), np.array([[ 3,  6], [ 9, 12]]))


def test_container_flatten_key_chains(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': {'d': ivy.array([2], dev=dev)},
                                 'e': {'f': {'g': ivy.array([3], dev=dev)}}}})

    # full
    container_flat = container.flatten_key_chains()
    assert np.allclose(ivy.to_numpy(container_flat['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat['b__c__d']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat.b__c__d), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat['b__e__f__g']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_flat.b__e__f__g), np.array([[3]]))

    # above height 1
    container_flat = container.flatten_key_chains(above_height=1)
    assert np.allclose(ivy.to_numpy(container_flat['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat['b__c']['d']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat.b__c.d), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat['b__e__f']['g']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_flat.b__e__f.g), np.array([[3]]))

    # below depth 1
    container_flat = container.flatten_key_chains(below_depth=1)
    assert np.allclose(ivy.to_numpy(container_flat['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat['b']['c__d']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat.b.c__d), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat['b']['e__f__g']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_flat.b.e__f__g), np.array([[3]]))

    # above height 1, below depth 1
    container_flat = container.flatten_key_chains(above_height=1, below_depth=1)
    assert np.allclose(ivy.to_numpy(container_flat['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_flat['b']['c']['d']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat.b.c.d), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_flat['b']['e__f']['g']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_flat.b.e__f.g), np.array([[3]]))


def test_container_deep_copy(dev, call):
    dict_in = {'a': ivy.array([0.], dev=dev),
               'b': {'c': ivy.array([1.], dev=dev), 'd': ivy.array([2.], dev=dev)}}
    cont = Container(dict_in)
    cont_deepcopy = cont.deep_copy()
    assert np.allclose(ivy.to_numpy(cont.a), ivy.to_numpy(cont_deepcopy.a))
    assert np.allclose(ivy.to_numpy(cont.b.c), ivy.to_numpy(cont_deepcopy.b.c))
    assert np.allclose(ivy.to_numpy(cont.b.d), ivy.to_numpy(cont_deepcopy.b.d))
    assert id(cont.a) != id(cont_deepcopy.a)
    assert id(cont.b.c) != id(cont_deepcopy.b.c)
    assert id(cont.b.d) != id(cont_deepcopy.b.d)


def test_container_contains(dev, call):
    arr0 = ivy.array([0.], dev=dev)
    arr1 = ivy.array([1.], dev=dev)
    arr2 = ivy.array([2.], dev=dev)
    sub_cont = Container({'c': arr1, 'd': arr2})
    container = Container({'a': arr0, 'b': sub_cont})

    # keys
    assert 'a' in container
    assert 'b' in container
    assert 'c' not in container
    assert 'b/c' in container
    assert 'd' not in container
    assert 'b/d' in container

    # sub-container
    assert container.contains_sub_container(container)
    assert container.contains_sub_container(sub_cont)
    assert sub_cont in container

    # partial sub-container
    partial_sub_cont = Container({'b': {'d': arr2}})
    assert container.contains_sub_container(container, partial=True)
    assert container.contains_sub_container(partial_sub_cont, partial=True)
    assert not partial_sub_cont.contains_sub_container(container, partial=True)

    # sub-structure
    sub_struc = Container({'c': ivy.array([3.], dev=dev), 'd': ivy.array([4.], dev=dev)})
    assert not container.contains_sub_container(sub_struc)
    assert sub_struc not in container
    assert container.contains_sub_structure(sub_struc)
    assert container.contains_sub_structure(container)

    # partial sub-structure
    partial_sub_struc = Container({'b': {'d': ivy.array([4.], dev=dev)}})
    assert container.contains_sub_structure(container, partial=True)
    assert container.contains_sub_structure(partial_sub_struc, partial=True)
    assert not partial_sub_struc.contains_sub_structure(container, partial=True)


def test_container_shuffle(dev, call):
    if call is helpers.tf_graph_call:
        # tf.random.set_seed is not compiled. The shuffle is then not aligned between container items.
        pytest.skip()
    dict_in = {'a': ivy.array([1, 2, 3], dev=dev),
               'b': {'c': ivy.array([1, 2, 3], dev=dev), 'd': ivy.array([1, 2, 3], dev=dev)}}
    container = Container(dict_in)

    # without key_chains specification
    container_shuffled = container.shuffle(0)
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert (ivy.to_numpy(container_shuffled['a']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.a) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['c']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['d']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.d) == shuffled_data).all()

    # with key_chains to apply
    container_shuffled = container.shuffle(0, ['a', 'b/c'])
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert (ivy.to_numpy(container_shuffled['a']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.a) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['c']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['d']) == ivy.to_numpy(data)).all()
    assert (ivy.to_numpy(container_shuffled.b.d) == ivy.to_numpy(data)).all()

    # with key_chains to apply pruned
    container_shuffled = container.shuffle(0, ['a', 'b/c'], prune_unapplied=True)
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert (ivy.to_numpy(container_shuffled['a']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.a) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['c']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == shuffled_data).all()
    assert 'b/d' not in container_shuffled

    # with key_chains to not apply pruned
    container_shuffled = container.shuffle(0, Container({'a': None, 'b': {'d': None}}), to_apply=False)
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert (ivy.to_numpy(container_shuffled['a']) == ivy.to_numpy(data)).all()
    assert (ivy.to_numpy(container_shuffled.a) == ivy.to_numpy(data)).all()
    assert (ivy.to_numpy(container_shuffled['b']['c']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b']['d']) == ivy.to_numpy(data)).all()
    assert (ivy.to_numpy(container_shuffled.b.d) == ivy.to_numpy(data)).all()

    # with key_chains to not apply pruned
    container_shuffled = container.shuffle(0, Container({'a': None, 'b': {'d': None}}), to_apply=False,
                                           prune_unapplied=True)
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert 'a' not in container_shuffled
    assert (ivy.to_numpy(container_shuffled['b']['c']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == shuffled_data).all()
    assert 'b/d' not in container_shuffled

    # map sequences
    dict_in = {'a': ivy.array([1, 2, 3], dev=dev),
               'b': [ivy.array([1, 2, 3], dev=dev), ivy.array([1, 2, 3], dev=dev)]}
    container = Container(dict_in)
    container_shuffled = container.shuffle(0, map_sequences=True)
    data = ivy.array([1, 2, 3], dev=dev)
    ivy.functional.ivy.random.seed()
    shuffled_data = ivy.to_numpy(ivy.functional.ivy.random.shuffle(data))
    assert (ivy.to_numpy(container_shuffled['a']) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.a) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b'][0]) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b[0]) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled['b'][1]) == shuffled_data).all()
    assert (ivy.to_numpy(container_shuffled.b[1]) == shuffled_data).all()


@pytest.mark.parametrize(
    "include_empty", [True, False])
def test_container_to_iterator(include_empty, dev, call):
    a_val = Container() if include_empty else ivy.array([1], dev=dev)
    bc_val = Container() if include_empty else ivy.array([2], dev=dev)
    bd_val = Container() if include_empty else ivy.array([3], dev=dev)
    dict_in = {'a': a_val, 'b': {'c': bc_val, 'd': bd_val}}
    container = Container(dict_in)

    # with key chains
    container_iterator = container.to_iterator(include_empty=include_empty)
    for (key_chain, value), expected in zip(container_iterator, [('a', a_val), ('b/c', bc_val), ('b/d', bd_val)]):
        expected_key_chain = expected[0]
        expected_value = expected[1]
        assert key_chain == expected_key_chain
        assert value is expected_value

    # with leaf keys
    container_iterator = container.to_iterator(leaf_keys_only=True, include_empty=include_empty)
    for (key_chain, value), expected in zip(container_iterator, [('a', a_val), ('c', bc_val), ('d', bd_val)]):
        expected_key_chain = expected[0]
        expected_value = expected[1]
        assert key_chain == expected_key_chain
        assert value is expected_value


@pytest.mark.parametrize(
    "include_empty", [True, False])
def test_container_to_iterator_values(include_empty, dev, call):
    a_val = Container() if include_empty else ivy.array([1], dev=dev)
    bc_val = Container() if include_empty else ivy.array([2], dev=dev)
    bd_val = Container() if include_empty else ivy.array([3], dev=dev)
    dict_in = {'a': a_val, 'b': {'c': bc_val, 'd': bd_val}}
    container = Container(dict_in)

    # with key chains
    container_iterator = container.to_iterator_values(include_empty=include_empty)
    for value, expected_value in zip(container_iterator, [a_val, bc_val, bd_val]):
        assert value is expected_value


@pytest.mark.parametrize(
    "include_empty", [True, False])
def test_container_to_iterator_keys(include_empty, dev, call):
    a_val = Container() if include_empty else ivy.array([1], dev=dev)
    bc_val = Container() if include_empty else ivy.array([2], dev=dev)
    bd_val = Container() if include_empty else ivy.array([3], dev=dev)
    dict_in = {'a': a_val, 'b': {'c': bc_val, 'd': bd_val}}
    container = Container(dict_in)

    # with key chains
    container_iterator = container.to_iterator_keys(include_empty=include_empty)
    for key_chain, expected_key_chain in zip(container_iterator, ['a', 'b/c', 'b/d']):
        assert key_chain == expected_key_chain

    # with leaf keys
    container_iterator = container.to_iterator_keys(leaf_keys_only=True, include_empty=include_empty)
    for key, expected_key in zip(container_iterator, ['a', 'c', 'd']):
        assert key == expected_key


def test_container_to_flat_list(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    container_flat_list = container.to_flat_list()
    for value, expected_value in zip(container_flat_list,
                                     [ivy.array([1], dev=dev), ivy.array([2], dev=dev),
                                      ivy.array([3], dev=dev)]):
        assert value == expected_value


def test_container_from_flat_list(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    flat_list = [4, 5, 6]
    container = container.from_flat_list(flat_list)
    assert np.allclose(ivy.to_numpy(container['a']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([6]))


@pytest.mark.parametrize(
    "inplace", [True, False])
def test_container_map(inplace, dev, call):
    # without key_chains specification
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container_orig = Container(dict_in)
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, inplace=inplace)
    if inplace:
        container_iterator = container.to_iterator()
    else:
        container_iterator = container_mapped.to_iterator()
    for (key, value), expected_value in zip(container_iterator,
                                            [ivy.array([2], dev=dev), ivy.array([3], dev=dev),
                                             ivy.array([4], dev=dev)]):
        assert call(lambda x: x, value) == call(lambda x: x, expected_value)

    # with key_chains to apply
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, ['a', 'b/c'], inplace=inplace)
    if inplace:
        container_mapped = container
    assert np.allclose(ivy.to_numpy(container_mapped['a']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_mapped.a), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['c']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.c), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.d), np.array([[3]]))

    # with key_chains to apply pruned
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, ['a', 'b/c'], prune_unapplied=True, inplace=inplace)
    if inplace:
        container_mapped = container
    assert np.allclose(ivy.to_numpy(container_mapped['a']), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_mapped.a), np.array([[2]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['c']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.c), np.array([[3]]))
    if not inplace:
        assert 'b/d' not in container_mapped

    # with key_chains to not apply
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, Container({'a': None, 'b': {'d': None}}), to_apply=False,
                                     inplace=inplace)
    if inplace:
        container_mapped = container
    assert np.allclose(ivy.to_numpy(container_mapped['a']), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_mapped.a), np.array([[1]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['c']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.c), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['d']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.d), np.array([[3]]))

    # with key_chains to not apply pruned
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, Container({'a': None, 'b': {'d': None}}), to_apply=False,
                                     prune_unapplied=True, inplace=inplace)
    if inplace:
        container_mapped = container
    if not inplace:
        assert 'a' not in container_mapped
    assert np.allclose(ivy.to_numpy(container_mapped['b']['c']), np.array([[3]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.c), np.array([[3]]))
    if not inplace:
        assert 'b/d' not in container_mapped

    # with sequences
    container_orig = Container({'a': ivy.array([1], dev=dev),
                                'b': [ivy.array([2], dev=dev), ivy.array([3], dev=dev)]})
    container = container_orig.deep_copy()
    container_mapped = container.map(lambda x, _: x + 1, inplace=inplace, map_sequences=True)
    if inplace:
        container_mapped = container
    assert np.allclose(ivy.to_numpy(container_mapped['a']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container_mapped['b'][0]), np.array([3]))
    assert np.allclose(ivy.to_numpy(container_mapped['b'][1]), np.array([4]))


@pytest.mark.parametrize(
    "inplace", [True, False])
def test_container_map_conts(inplace, dev, call):
    # without key_chains specification
    container_orig = Container({'a': ivy.array([1], dev=dev),
                                'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})

    def _add_e_attr(cont_in):
        cont_in.e = ivy.array([4], dev=dev)
        return cont_in

    # with self
    container = container_orig.deep_copy()
    container_mapped = container.map_conts(lambda c, _: _add_e_attr(c), inplace=inplace)
    if inplace:
        container_mapped = container
    assert 'e' in container_mapped
    assert np.array_equal(ivy.to_numpy(container_mapped.e), np.array([4]))
    assert 'e' in container_mapped.b
    assert np.array_equal(ivy.to_numpy(container_mapped.b.e), np.array([4]))

    # without self
    container = container_orig.deep_copy()
    container_mapped = container.map_conts(lambda c, _: _add_e_attr(c), include_self=False, inplace=inplace)
    if inplace:
        container_mapped = container
    assert 'e' not in container_mapped
    assert 'e' in container_mapped.b
    assert np.array_equal(ivy.to_numpy(container_mapped.b.e), np.array([4]))


def test_container_multi_map(dev, call):
    # without key_chains specification
    container0 = Container({'a': ivy.array([1], dev=dev),
                            'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container1 = Container({'a': ivy.array([3], dev=dev),
                            'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([5], dev=dev)}})

    # with key_chains to apply
    container_mapped = ivy.Container.multi_map(lambda x, _: x[0] + x[1], [container0, container1])
    assert np.allclose(ivy.to_numpy(container_mapped['a']), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_mapped.a), np.array([[4]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['c']), np.array([[6]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.c), np.array([[6]]))
    assert np.allclose(ivy.to_numpy(container_mapped['b']['d']), np.array([[8]]))
    assert np.allclose(ivy.to_numpy(container_mapped.b.d), np.array([[8]]))


def test_container_common_key_chains(dev, call):
    arr1 = ivy.array([1], dev=dev)
    arr2 = ivy.array([2], dev=dev)
    arr3 = ivy.array([3], dev=dev)
    cont0 = Container({'a': arr1, 'b': {'c': arr2, 'd': arr3}})
    cont1 = Container({'b': {'c': arr2, 'd': arr3, 'e': arr1}})
    cont2 = Container({'a': arr1, 'b': {'d': arr3, 'e': arr1}})

    # 0
    common_kcs = Container.common_key_chains([cont0])
    assert len(common_kcs) == 3
    assert 'a' in common_kcs
    assert 'b/c' in common_kcs
    assert 'b/d' in common_kcs

    # 0-1
    common_kcs = Container.common_key_chains([cont0, cont1])
    assert len(common_kcs) == 2
    assert 'b/c' in common_kcs
    assert 'b/d' in common_kcs

    # 0-2
    common_kcs = Container.common_key_chains([cont0, cont2])
    assert len(common_kcs) == 2
    assert 'a' in common_kcs
    assert 'b/d' in common_kcs

    # 1-2
    common_kcs = Container.common_key_chains([cont1, cont2])
    assert len(common_kcs) == 2
    assert 'b/d' in common_kcs
    assert 'b/e' in common_kcs

    # all
    common_kcs = Container.common_key_chains([cont0, cont1, cont2])
    assert len(common_kcs) == 1
    assert 'b/d' in common_kcs


def test_container_identical(dev, call):
    # without key_chains specification
    arr1 = ivy.array([1], dev=dev)
    arr2 = ivy.array([2], dev=dev)
    arr3 = ivy.array([3], dev=dev)
    container0 = Container({'a': arr1, 'b': {'c': arr2, 'd': arr3}})
    container1 = Container({'a': arr1, 'b': {'c': arr2, 'd': arr3}})
    container2 = Container({'a': ivy.array([1], dev=dev),
                            'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container3 = Container({'b': {'d': arr3}})
    container4 = Container({'d': arr3})

    # the same
    assert ivy.Container.identical([container0, container1])
    assert ivy.Container.identical([container1, container0])

    # not the same
    assert not ivy.Container.identical([container0, container2])
    assert not ivy.Container.identical([container2, container0])
    assert not ivy.Container.identical([container1, container2])
    assert not ivy.Container.identical([container2, container1])

    # partial
    assert ivy.Container.identical([container0, container3], partial=True)
    assert ivy.Container.identical([container3, container0], partial=True)
    assert not ivy.Container.identical([container0, container4], partial=True)
    assert not ivy.Container.identical([container4, container0], partial=True)


def test_container_identical_structure(dev, call):
    # without key_chains specification
    container0 = Container({'a': ivy.array([1], dev=dev),
                            'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container1 = Container({'a': ivy.array([3], dev=dev),
                            'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container2 = Container({'a': ivy.array([3], dev=dev),
                            'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([5], dev=dev),
                                  'e': ivy.array([6], dev=dev)}})
    container3 = Container({'a': ivy.array([3], dev=dev),
                            'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([5], dev=dev)},
                            'e': ivy.array([6], dev=dev)})
    container4 = Container({'b': {'d': ivy.array([4], dev=dev)}})
    container5 = Container({'d': ivy.array([4], dev=dev)})

    # with identical
    assert ivy.Container.identical_structure([container0, container1])
    assert ivy.Container.identical_structure([container1, container0])
    assert ivy.Container.identical_structure([container1, container0, container1])

    # without identical
    assert not ivy.Container.identical_structure([container2, container3])
    assert not ivy.Container.identical_structure([container0, container3])
    assert not ivy.Container.identical_structure([container1, container2])
    assert not ivy.Container.identical_structure([container1, container0, container2])

    # partial
    assert ivy.Container.identical_structure([container0, container4], partial=True)
    assert ivy.Container.identical_structure([container1, container4], partial=True)
    assert ivy.Container.identical_structure([container2, container4], partial=True)
    assert ivy.Container.identical_structure([container3, container4], partial=True)
    assert ivy.Container.identical_structure([container4, container4], partial=True)
    assert not ivy.Container.identical_structure([container0, container5], partial=True)
    assert not ivy.Container.identical_structure([container1, container5], partial=True)
    assert not ivy.Container.identical_structure([container2, container5], partial=True)
    assert not ivy.Container.identical_structure([container3, container5], partial=True)
    assert not ivy.Container.identical_structure([container4, container5], partial=True)


def test_container_identical_configs(dev, call):
    container0 = Container({'a': ivy.array([1], dev=dev)}, print_limit=5)
    container1 = Container({'a': ivy.array([1], dev=dev)}, print_limit=5)
    container2 = Container({'a': ivy.array([1], dev=dev)}, print_limit=10)

    # with identical
    assert ivy.Container.identical_configs([container0, container1])
    assert ivy.Container.identical_configs([container1, container0])
    assert ivy.Container.identical_configs([container1, container0, container1])

    # without identical
    assert not ivy.Container.identical_configs([container1, container2])
    assert not ivy.Container.identical_configs([container1, container0, container2])


def test_container_identical_array_shapes(dev, call):
    # without key_chains specification
    container0 = Container({'a': ivy.array([1, 2], dev=dev),
                            'b': {'c': ivy.array([2, 3, 4], dev=dev),
                                  'd': ivy.array([3, 4, 5, 6], dev=dev)}})
    container1 = Container({'a': ivy.array([1, 2, 3, 4], dev=dev),
                            'b': {'c': ivy.array([3, 4], dev=dev),
                                  'd': ivy.array([3, 4, 5], dev=dev)}})
    container2 = Container({'a': ivy.array([1, 2, 3, 4], dev=dev),
                            'b': {'c': ivy.array([3, 4], dev=dev),
                                  'd': ivy.array([3, 4, 5, 6], dev=dev)}})

    # with identical
    assert ivy.Container.identical_array_shapes([container0, container1])
    assert ivy.Container.identical_array_shapes([container1, container0])
    assert ivy.Container.identical_array_shapes([container1, container0, container1])
    assert not ivy.Container.identical([container0, container2])
    assert not ivy.Container.identical([container1, container2])
    assert not ivy.Container.identical([container0, container1, container2])


def test_container_dtype(dev, call):
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2.], dev=dev), 'd': ivy.array([3], dev=dev)}}
    container = Container(dict_in)
    dtype_container = container.dtype()
    for (key, value), expected_value in zip(dtype_container.to_iterator(),
                                            [ivy.array([1], dev=dev).dtype,
                                             ivy.array([2.], dev=dev).dtype,
                                             ivy.array([3], dev=dev).dtype]):
        assert value == expected_value


def test_container_with_entries_as_lists(dev, call):
    if call in [helpers.tf_graph_call]:
        # to_list() requires eager execution
        pytest.skip()
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2.], dev=dev), 'd': 'some string'}}
    container = Container(dict_in)
    container_w_list_entries = container.with_entries_as_lists()
    for (key, value), expected_value in zip(container_w_list_entries.to_iterator(),
                                            [[1],
                                             [2.],
                                             'some string']):
        assert value == expected_value


def test_container_reshape_like(dev, call):
    container = Container({'a': ivy.array([[1.]], dev=dev),
                           'b': {'c': ivy.array([[3.], [4.]], dev=dev),
                                 'd': ivy.array([[5.], [6.], [7.]], dev=dev)}})
    new_shapes = Container({'a': (1,),
                            'b': {'c': (1, 2, 1), 'd': (3, 1, 1)}})

    # without leading shape
    container_reshaped = container.reshape_like(new_shapes)
    assert list(container_reshaped['a'].shape) == [1]
    assert list(container_reshaped.a.shape) == [1]
    assert list(container_reshaped['b']['c'].shape) == [1, 2, 1]
    assert list(container_reshaped.b.c.shape) == [1, 2, 1]
    assert list(container_reshaped['b']['d'].shape) == [3, 1, 1]
    assert list(container_reshaped.b.d.shape) == [3, 1, 1]

    # with leading shape
    container = Container({'a': ivy.array([[[1.]], [[1.]], [[1.]]], dev=dev),
                           'b': {'c': ivy.array([[[3.], [4.]], [[3.], [4.]], [[3.], [4.]]], dev=dev),
                                 'd': ivy.array([[[5.], [6.], [7.]], [[5.], [6.], [7.]], [[5.], [6.], [7.]]],
                                                dev=dev)}})
    container_reshaped = container.reshape_like(new_shapes, leading_shape=[3])
    assert list(container_reshaped['a'].shape) == [3, 1]
    assert list(container_reshaped.a.shape) == [3, 1]
    assert list(container_reshaped['b']['c'].shape) == [3, 1, 2, 1]
    assert list(container_reshaped.b.c.shape) == [3, 1, 2, 1]
    assert list(container_reshaped['b']['d'].shape) == [3, 3, 1, 1]
    assert list(container_reshaped.b.d.shape) == [3, 3, 1, 1]


def test_container_slice(dev, call):
    dict_in = {'a': ivy.array([[0.], [1.]], dev=dev),
               'b': {'c': ivy.array([[1.], [2.]], dev=dev), 'd': ivy.array([[2.], [3.]], dev=dev)}}
    container = Container(dict_in)
    container0 = container[0]
    container1 = container[1]
    assert np.array_equal(ivy.to_numpy(container0['a']), np.array([0.]))
    assert np.array_equal(ivy.to_numpy(container0.a), np.array([0.]))
    assert np.array_equal(ivy.to_numpy(container0['b']['c']), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(container0.b.c), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(container0['b']['d']), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(container0.b.d), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(container1['a']), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(container1.a), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(container1['b']['c']), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(container1.b.c), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(container1['b']['d']), np.array([3.]))
    assert np.array_equal(ivy.to_numpy(container1.b.d), np.array([3.]))


def test_container_slice_via_key(dev, call):
    dict_in = {'a': {'x': ivy.array([0.], dev=dev),
                     'y': ivy.array([1.], dev=dev)},
               'b': {'c': {'x': ivy.array([1.], dev=dev),
                           'y': ivy.array([2.], dev=dev)},
                     'd': {'x': ivy.array([2.], dev=dev),
                           'y': ivy.array([3.], dev=dev)}}}
    container = Container(dict_in)
    containerx = container.slice_via_key('x')
    containery = container.slice_via_key('y')
    assert np.array_equal(ivy.to_numpy(containerx['a']), np.array([0.]))
    assert np.array_equal(ivy.to_numpy(containerx.a), np.array([0.]))
    assert np.array_equal(ivy.to_numpy(containerx['b']['c']), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(containerx.b.c), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(containerx['b']['d']), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(containerx.b.d), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(containery['a']), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(containery.a), np.array([1.]))
    assert np.array_equal(ivy.to_numpy(containery['b']['c']), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(containery.b.c), np.array([2.]))
    assert np.array_equal(ivy.to_numpy(containery['b']['d']), np.array([3.]))
    assert np.array_equal(ivy.to_numpy(containery.b.d), np.array([3.]))


def test_container_to_and_from_disk_as_hdf5(dev, call):
    if call in [helpers.tf_graph_call]:
        # container disk saving requires eager execution
        pytest.skip()
    save_filepath = 'container_on_disk.hdf5'
    dict_in_1 = {'a': ivy.array([np.float32(1.)], dev=dev),
                 'b': {'c': ivy.array([np.float32(2.)], dev=dev),
                       'd': ivy.array([np.float32(3.)], dev=dev)}}
    container1 = Container(dict_in_1)
    dict_in_2 = {'a': ivy.array([np.float32(1.), np.float32(1.)], dev=dev),
                 'b': {'c': ivy.array([np.float32(2.), np.float32(2.)], dev=dev),
                       'd': ivy.array([np.float32(3.), np.float32(3.)], dev=dev)}}
    container2 = Container(dict_in_2)

    # saving
    container1.to_disk_as_hdf5(save_filepath, max_batch_size=2)
    assert os.path.exists(save_filepath)

    # loading
    loaded_container = Container.from_disk_as_hdf5(save_filepath, slice(1))
    assert np.array_equal(ivy.to_numpy(loaded_container.a), ivy.to_numpy(container1.a))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.c), ivy.to_numpy(container1.b.c))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.d), ivy.to_numpy(container1.b.d))

    # appending
    container1.to_disk_as_hdf5(save_filepath, max_batch_size=2, starting_index=1)
    assert os.path.exists(save_filepath)

    # loading after append
    loaded_container = Container.from_disk_as_hdf5(save_filepath)
    assert np.array_equal(ivy.to_numpy(loaded_container.a), ivy.to_numpy(container2.a))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.c), ivy.to_numpy(container2.b.c))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.d), ivy.to_numpy(container2.b.d))

    # load slice
    loaded_sliced_container = Container.from_disk_as_hdf5(save_filepath, slice(1, 2))
    assert np.array_equal(ivy.to_numpy(loaded_sliced_container.a), ivy.to_numpy(container1.a))
    assert np.array_equal(ivy.to_numpy(loaded_sliced_container.b.c), ivy.to_numpy(container1.b.c))
    assert np.array_equal(ivy.to_numpy(loaded_sliced_container.b.d), ivy.to_numpy(container1.b.d))

    # file size
    file_size, batch_size = Container.h5_file_size(save_filepath)
    assert file_size == 6 * np.dtype(np.float32).itemsize
    assert batch_size == 2

    os.remove(save_filepath)


def test_container_to_disk_shuffle_and_from_disk_as_hdf5(dev, call):
    if call in [helpers.tf_graph_call]:
        # container disk saving requires eager execution
        pytest.skip()
    save_filepath = 'container_on_disk.hdf5'
    dict_in = {'a': ivy.array([1, 2, 3], dev=dev),
               'b': {'c': ivy.array([1, 2, 3], dev=dev), 'd': ivy.array([1, 2, 3], dev=dev)}}
    container = Container(dict_in)

    # saving
    container.to_disk_as_hdf5(save_filepath, max_batch_size=3)
    assert os.path.exists(save_filepath)

    # shuffling
    Container.shuffle_h5_file(save_filepath)

    # loading
    container_shuffled = Container.from_disk_as_hdf5(save_filepath, slice(3))

    # testing
    data = np.array([1, 2, 3])
    random.seed(0)
    random.shuffle(data)

    assert (ivy.to_numpy(container_shuffled['a']) == data).all()
    assert (ivy.to_numpy(container_shuffled.a) == data).all()
    assert (ivy.to_numpy(container_shuffled['b']['c']) == data).all()
    assert (ivy.to_numpy(container_shuffled.b.c) == data).all()
    assert (ivy.to_numpy(container_shuffled['b']['d']) == data).all()
    assert (ivy.to_numpy(container_shuffled.b.d) == data).all()

    os.remove(save_filepath)


# def test_container_pickle(dev, call):
#     if call in [helpers.tf_graph_call]:
#         # container disk saving requires eager execution
#         pytest.skip()
#     dict_in = {'a': ivy.array([np.float32(1.)], dev=dev),
#                'b': {'c': ivy.array([np.float32(2.)], dev=dev),
#                      'd': ivy.array([np.float32(3.)], dev=dev)}}
#
#     # without module attribute
#     cont = Container(dict_in)
#     assert cont._local_ivy is None
#     pickled = pickle.dumps(cont)
#     cont_again = pickle.loads(pickled)
#     assert cont_again._local_ivy is None
#     ivy.Container.identical_structure([cont, cont_again])
#     ivy.Container.identical_configs([cont, cont_again])
#
#     # with module attribute
#     cont = Container(dict_in, ivyh=ivy)
#     assert cont._local_ivy is ivy
#     pickled = pickle.dumps(cont)
#     cont_again = pickle.loads(pickled)
#     # noinspection PyUnresolvedReferences
#     assert cont_again._local_ivy.current_framework_str() is ivy.current_framework_str()
#     ivy.Container.identical_structure([cont, cont_again])
#     ivy.Container.identical_configs([cont, cont_again])


def test_container_to_and_from_disk_as_pickled(dev, call):
    if call in [helpers.tf_graph_call]:
        # container disk saving requires eager execution
        pytest.skip()
    save_filepath = 'container_on_disk.pickled'
    dict_in = {'a': ivy.array([np.float32(1.)], dev=dev),
               'b': {'c': ivy.array([np.float32(2.)], dev=dev),
                     'd': ivy.array([np.float32(3.)], dev=dev)}}
    container = Container(dict_in)

    # saving
    container.to_disk_as_pickled(save_filepath)
    assert os.path.exists(save_filepath)

    # loading
    loaded_container = Container.from_disk_as_pickled(save_filepath)
    assert np.array_equal(ivy.to_numpy(loaded_container.a), ivy.to_numpy(container.a))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.c), ivy.to_numpy(container.b.c))
    assert np.array_equal(ivy.to_numpy(loaded_container.b.d), ivy.to_numpy(container.b.d))

    os.remove(save_filepath)


def test_container_to_and_from_disk_as_json(dev, call):
    if call in [helpers.tf_graph_call]:
        # container disk saving requires eager execution
        pytest.skip()
    save_filepath = 'container_on_disk.json'
    dict_in = {'a': 1.274e-7, 'b': {'c': True, 'd': ivy.array([np.float32(3.)], dev=dev)}}
    container = Container(dict_in)

    # saving
    container.to_disk_as_json(save_filepath)
    assert os.path.exists(save_filepath)

    # loading
    loaded_container = Container.from_disk_as_json(save_filepath)
    assert np.array_equal(loaded_container.a, container.a)
    assert np.array_equal(loaded_container.b.c, container.b.c)
    assert isinstance(loaded_container.b.d, str)

    os.remove(save_filepath)


def test_container_positive(dev, call):
    container = +Container({'a': ivy.array([1], dev=dev),
                            'b': {'c': ivy.array([-2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([-2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([-2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([3]))


def test_container_negative(dev, call):
    container = -Container({'a': ivy.array([1], dev=dev),
                            'b': {'c': ivy.array([-2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([-1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([-1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([-3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([-3]))


def test_container_pow(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container = container_a ** container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([16]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([16]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([729]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([729]))


def test_container_scalar_pow(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container_a ** 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([9]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([9]))


def test_container_reverse_scalar_pow(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 ** container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([8]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([8]))


def test_container_scalar_addition(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container += 3
    assert np.allclose(ivy.to_numpy(container['a']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([6]))


def test_container_reverse_scalar_addition(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 3 + container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([4]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([4]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([6]))


def test_container_addition(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container = container_a + container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([6]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([9]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([9]))


def test_container_scalar_subtraction(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container -= 1
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([2]))


def test_container_reverse_scalar_subtraction(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 1 - container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([-1]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([-1]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([-2]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([-2]))


def test_container_subtraction(dev, call):
    container_a = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container_b = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([1], dev=dev), 'd': ivy.array([4], dev=dev)}})
    container = container_a - container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([2]))


def test_container_sum(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container = sum([container_a, container_b])
    assert np.allclose(ivy.to_numpy(container['a']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([3]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([6]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([6]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([9]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([9]))


def test_container_scalar_multiplication(dev, call):
    container = Container({'a': ivy.array([1.], dev=dev),
                           'b': {'c': ivy.array([2.], dev=dev), 'd': ivy.array([3.], dev=dev)}})
    container *= 2.5
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5.]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5.]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([7.5]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([7.5]))


def test_container_reverse_scalar_multiplication(dev, call):
    container = Container({'a': ivy.array([1.], dev=dev),
                           'b': {'c': ivy.array([2.], dev=dev), 'd': ivy.array([3.], dev=dev)}})
    container = 2.5 * container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5.]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5.]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([7.5]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([7.5]))


def test_container_multiplication(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([4], dev=dev), 'd': ivy.array([6], dev=dev)}})
    container = container_a * container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([8]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([8]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([18]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([18]))


def test_container_scalar_truediv(dev, call):
    container = Container({'a': ivy.array([1.], dev=dev),
                           'b': {'c': ivy.array([5.], dev=dev), 'd': ivy.array([5.], dev=dev)}})
    container /= 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0.5]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0.5]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([2.5]))


def test_container_reverse_scalar_truediv(dev, call):
    container = Container({'a': ivy.array([1.], dev=dev),
                           'b': {'c': ivy.array([5.], dev=dev), 'd': ivy.array([5.], dev=dev)}})
    container = 2 / container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2.]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2.]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([0.4]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([0.4]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([0.4]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([0.4]))


def test_container_truediv(dev, call):
    container_a = Container({'a': ivy.array([1.], dev=dev),
                             'b': {'c': ivy.array([5.], dev=dev), 'd': ivy.array([5.], dev=dev)}})
    container_b = Container({'a': ivy.array([2.], dev=dev),
                             'b': {'c': ivy.array([2.], dev=dev), 'd': ivy.array([4.], dev=dev)}})
    container = container_a / container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0.5]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0.5]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2.5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([1.25]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([1.25]))


def test_container_scalar_floordiv(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the // operator, can add if explicit ivy.floordiv is implemented at some point
        pytest.skip()
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container //= 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([2]))


def test_container_reverse_scalar_floordiv(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the // operator, can add if explicit ivy.floordiv is implemented at some point
        pytest.skip()
    container = Container({'a': ivy.array([2], dev=dev),
                           'b': {'c': ivy.array([1], dev=dev), 'd': ivy.array([7], dev=dev)}})
    container = 5 // container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([5]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([5]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([0]))


def test_container_floordiv(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the // operator, can add if explicit ivy.floordiv is implemented at some point
        pytest.skip()
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([4], dev=dev)}})
    container = container_a // container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([0]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([0]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([1]))


def test_container_abs(dev, call):
    container = abs(Container({'a': ivy.array([1], dev=dev),
                               'b': {'c': ivy.array([-2], dev=dev), 'd': ivy.array([3], dev=dev)}}))
    assert np.allclose(ivy.to_numpy(container['a']), np.array([1]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([1]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([2]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([2]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([3]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([3]))


def test_container_scalar_less_than(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container < 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_reverse_scalar_less_than(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 < container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_less_than(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a < container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_scalar_less_than_or_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container <= 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_reverse_scalar_less_than_or_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 <= container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_less_than_or_equal_to(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a <= container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_scalar_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container == 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_reverse_scalar_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 == container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_equal_to(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a == container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_scalar_not_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container != 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))

    
def test_container_reverse_scalar_not_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 != container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_not_equal_to(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a != container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_scalar_greater_than(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container > 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_reverse_scalar_greater_than(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 > container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_greater_than(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a > container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_scalar_greater_than_or_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = container >= 2
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_reverse_scalar_greater_than_or_equal_to(dev, call):
    container = Container({'a': ivy.array([1], dev=dev),
                           'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}})
    container = 2 >= container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_greater_than_or_equal_to(dev, call):
    container_a = Container({'a': ivy.array([1], dev=dev),
                             'b': {'c': ivy.array([5], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container_b = Container({'a': ivy.array([2], dev=dev),
                             'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([5], dev=dev)}})
    container = container_a >= container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_scalar_and(dev, call):
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container & True
    # ToDo: work out why "container and True" does not work. Perhaps bool(container) is called first implicitly?
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_reverse_scalar_and(dev, call):
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = True and container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_and(dev, call):
    container_a = Container({'a': ivy.array([True], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container_b = Container({'a': ivy.array([False], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container_a and container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_scalar_or(dev, call):
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container or False
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_reverse_scalar_or(dev, call):
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container or False
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_or(dev, call):
    container_a = Container({'a': ivy.array([True], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container_b = Container({'a': ivy.array([False], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container_a or container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_not(dev, call):
    container = ~Container({'a': ivy.array([True], dev=dev),
                            'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_scalar_xor(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the ^ operator, can add if explicit ivy.logical_xor is implemented at some point
        pytest.skip()
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container != True
    assert np.allclose(ivy.to_numpy(container['a']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([True]))


def test_container_reverse_scalar_xor(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the ^ operator, can add if explicit ivy.logical_xor is implemented at some point
        pytest.skip()
    container = Container({'a': ivy.array([True], dev=dev),
                           'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = False != container
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_xor(dev, call):
    if call is helpers.mx_call:
        # MXnet arrays do not overload the ^ operator, can add if explicit ivy.logical_xor is implemented at some point
        pytest.skip()
    container_a = Container({'a': ivy.array([True], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container_b = Container({'a': ivy.array([False], dev=dev),
                             'b': {'c': ivy.array([True], dev=dev), 'd': ivy.array([False], dev=dev)}})
    container = container_a != container_b
    assert np.allclose(ivy.to_numpy(container['a']), np.array([True]))
    assert np.allclose(ivy.to_numpy(container.a), np.array([True]))
    assert np.allclose(ivy.to_numpy(container['b']['c']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.c), np.array([False]))
    assert np.allclose(ivy.to_numpy(container['b']['d']), np.array([False]))
    assert np.allclose(ivy.to_numpy(container.b.d), np.array([False]))


def test_container_shape(dev, call):
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2.], [4.], [6.]]], dev=dev),
                     'd': ivy.array([[[3.], [6.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    assert container.shape == [1, 3, 1]
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2., 3.], [4., 5.], [6., 7.]]], dev=dev),
                     'd': ivy.array([[[3.], [6.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    assert container.shape == [1, 3, None]
    dict_in = {'a': ivy.array([[[1., 2.], [2., 3.], [3., 4.]]], dev=dev),
               'b': {'c': ivy.array([[[2., 3.], [4., 5.], [6., 7.]]], dev=dev),
                     'd': ivy.array([[[3., 4.], [6., 7.], [9., 10.]]], dev=dev)}}
    container = Container(dict_in)
    assert container.shape == [1, 3, 2]


def test_container_shapes(dev, call):
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2.], [4.]]], dev=dev), 'd': ivy.array([[9.]], dev=dev)}}
    container_shapes = Container(dict_in).shapes
    assert list(container_shapes['a']) == [1, 3, 1]
    assert list(container_shapes.a) == [1, 3, 1]
    assert list(container_shapes['b']['c']) == [1, 2, 1]
    assert list(container_shapes.b.c) == [1, 2, 1]
    assert list(container_shapes['b']['d']) == [1, 1]
    assert list(container_shapes.b.d) == [1, 1]


def test_container_dev_str(dev, call):
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2.], [4.], [6.]]], dev=dev),
                     'd': ivy.array([[[3.], [6.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    assert container.dev_str == dev


def test_container_create_if_absent(dev, call):
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2.], [4.], [6.]]], dev=dev),
                     'd': ivy.array([[[3.], [6.], [9.]]], dev=dev)}}

    # depth 1
    container = Container(dict_in)
    container.create_if_absent('a', None, True)
    assert np.allclose(ivy.to_numpy(container.a), np.array([[[1.], [2.], [3.]]]))
    container.create_if_absent('e', ivy.array([[[4.], [8.], [12.]]]), True)
    assert np.allclose(ivy.to_numpy(container.e), np.array([[[4.], [8.], [12.]]]))

    # depth 2
    container.create_if_absent('f/g', np.array([[[5.], [10.], [15.]]]), True)
    assert np.allclose(ivy.to_numpy(container.f.g), np.array([[[5.], [10.], [15.]]]))


def test_container_if_exists(dev, call):
    dict_in = {'a': ivy.array([[[1.], [2.], [3.]]], dev=dev),
               'b': {'c': ivy.array([[[2.], [4.], [6.]]], dev=dev),
                     'd': ivy.array([[[3.], [6.], [9.]]], dev=dev)}}
    container = Container(dict_in)
    assert np.allclose(ivy.to_numpy(container.if_exists('a')), np.array([[[1.], [2.], [3.]]]))
    assert 'c' not in container
    assert container.if_exists('c') is None
    container['c'] = ivy.array([[[1.], [2.], [3.]]], dev=dev)
    assert np.allclose(ivy.to_numpy(container.if_exists('c')), np.array([[[1.], [2.], [3.]]]))
    assert container.if_exists('d') is None
    container.d = ivy.array([[[1.], [2.], [3.]]], dev=dev)
    assert np.allclose(ivy.to_numpy(container.if_exists('d')), np.array([[[1.], [2.], [3.]]]))


def test_jax_pytree_compatibility(dev, call):

    if call is not helpers.jnp_call:
        pytest.skip()

    # import
    from jax.tree_util import tree_flatten

    # dict in
    dict_in = {'a': ivy.array([1], dev=dev),
               'b': {'c': ivy.array([2], dev=dev), 'd': ivy.array([3], dev=dev)}}

    # container
    container = Container(dict_in)

    # container flattened
    cont_values = tree_flatten(container)[0]

    # dict flattened
    true_values = tree_flatten(dict_in)[0]

    # assertion
    for i, true_val in enumerate(true_values):
        assert np.array_equal(ivy.to_numpy(cont_values[i]), ivy.to_numpy(true_val))


def test_container_from_queues(dev, call):

    if 'gpu' in dev:
        # Cannot re-initialize CUDA in forked subprocess. 'spawn' start method must be used.
        pytest.skip()

    if ivy.gpu_is_available() and call is helpers.jnp_call:
        # Not found a way to set default device for JAX, and this causes issues with multiprocessing and CUDA,
        # even when dev=cpu
        # ToDo: find a fix for this problem ^^
        pytest.skip()

    def worker_fn(in_queue, out_queue, load_size, worker_id):
        keep_going = True
        while keep_going:
            try:
                keep_going = in_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            out_queue.put({'a': [ivy.to_native(ivy.array([1., 2., 3.], dev=dev)) * worker_id] * load_size})

    workers = list()
    in_queues = list()
    out_queues = list()
    queue_load_sizes = [1, 2, 1]
    for i, queue_load_size in enumerate(queue_load_sizes):
        input_queue = multiprocessing.Queue()
        output_queue = multiprocessing.Queue()
        worker = multiprocessing.Process(target=worker_fn, args=(input_queue, output_queue, queue_load_size, i + 1))
        worker.start()
        in_queues.append(input_queue)
        out_queues.append(output_queue)
        workers.append(worker)

    container = Container(queues=out_queues, queue_load_sizes=queue_load_sizes, queue_timeout=0.25)

    # queue 0
    queue_was_empty = False
    try:
        container[0]
    except queue.Empty:
        queue_was_empty = True
    assert queue_was_empty
    in_queues[0].put(True)
    assert np.allclose(ivy.to_numpy(container[0].a), np.array([1., 2., 3.]))
    assert np.allclose(ivy.to_numpy(container[0].a), np.array([1., 2., 3.]))

    # queue 1
    queue_was_empty = False
    try:
        container[1]
    except queue.Empty:
        queue_was_empty = True
    assert queue_was_empty
    queue_was_empty = False
    try:
        container[2]
    except queue.Empty:
        queue_was_empty = True
    assert queue_was_empty
    in_queues[1].put(True)
    assert np.allclose(ivy.to_numpy(container[1].a), np.array([2., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container[1].a), np.array([2., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container[2].a), np.array([2., 4., 6.]))
    assert np.allclose(ivy.to_numpy(container[2].a), np.array([2., 4., 6.]))

    # queue 2
    queue_was_empty = False
    try:
        container[3]
    except queue.Empty:
        queue_was_empty = True
    assert queue_was_empty
    in_queues[2].put(True)
    assert np.allclose(ivy.to_numpy(container[3].a), np.array([3., 6., 9.]))
    assert np.allclose(ivy.to_numpy(container[3].a), np.array([3., 6., 9.]))

    # stop workers
    in_queues[0].put(False)
    in_queues[1].put(False)
    in_queues[2].put(False)
    in_queues[0].close()
    in_queues[1].close()
    in_queues[2].close()

    # join workers
    for worker in workers:
        worker.join()

    del container
