"""
Collection of tests for unified device functions
"""

# global
import math
import pytest
import numpy as np
from numbers import Number

# local
import ivy
import ivy.functional.backends.numpy
import ivy_tests.test_ivy.helpers as helpers


# Tests #
# ------#

# Device Queries #

# dev
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_dev(x, dtype, tensor_fn, dev, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == helpers.var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype, dev)
    ret = ivy.dev(x, as_str=True)
    # type test
    assert isinstance(ret, str)
    # value test
    assert ret == dev

# dev_to_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_dev_to_str(x, dtype, tensor_fn, dev, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == helpers.var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype, dev)
    dev = ivy.dev(x)
    ret = ivy.dev_to_str(dev)
    # type test
    assert isinstance(ret, str)


# dev_from_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_dev_from_str(x, dtype, tensor_fn, dev, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == helpers.var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype, dev)
    dev = ivy.dev_from_str(dev)
    ret = ivy.dev_from_str(ivy.dev(x, as_str=True))
    # value test
    if call in [helpers.tf_call, helpers.tf_graph_call]:
        assert '/' + ':'.join(ret[1:].split(':')[-2:]) == '/' + ':'.join(dev[1:].split(':')[-2:])
    elif call is helpers.torch_call:
        assert ret.type == dev.type
    else:
        assert ret == dev
    # compilation test
    if call is helpers.torch_call:
        # pytorch scripting does not handle converting string to device
        return



# memory_on_dev
@pytest.mark.parametrize(
    "dev_to_check", ['cpu', 'gpu:0'])
def test_memory_on_dev(dev_to_check, dev, call):
    if 'gpu' in dev_to_check and ivy.num_gpus() == 0:
        # cannot get amount of memory for gpu which is not present
        pytest.skip()
    ret = ivy.total_mem_on_dev(dev_to_check)
    # type test
    assert isinstance(ret, float)
    # value test
    assert 0 < ret < 64
    # compilation test
    if call is helpers.torch_call:
        # global variables aren't supported for pytorch scripting
        pytest.skip()


# Device Allocation #

# default_device
def test_default_device(dev, call):

    # setting and unsetting
    orig_len = len(ivy.default_device_stack)
    ivy.set_default_device('cpu')
    assert len(ivy.default_device_stack) == orig_len + 1
    ivy.set_default_device('cpu')
    assert len(ivy.default_device_stack) == orig_len + 2
    ivy.unset_default_device()
    assert len(ivy.default_device_stack) == orig_len + 1
    ivy.unset_default_device()
    assert len(ivy.default_device_stack) == orig_len

    # with
    assert len(ivy.default_device_stack) == orig_len
    with ivy.DefaultDevice('cpu'):
        assert len(ivy.default_device_stack) == orig_len + 1
        with ivy.DefaultDevice('cpu'):
            assert len(ivy.default_device_stack) == orig_len + 2
        assert len(ivy.default_device_stack) == orig_len + 1
    assert len(ivy.default_device_stack) == orig_len


# to_dev
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_to_dev(x, dtype, tensor_fn, dev, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == helpers.var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype, dev)
    dev = ivy.dev(x)
    x_on_dev = ivy.to_dev(x, dev)
    dev_from_new_x = ivy.dev(x)
    # value test
    if call in [helpers.tf_call, helpers.tf_graph_call]:
        assert '/' + ':'.join(dev_from_new_x[1:].split(':')[-2:]) == '/' + ':'.join(dev[1:].split(':')[-2:])
    elif call is helpers.torch_call:
        assert dev_from_new_x.type == dev.type
    else:
        assert dev_from_new_x == dev


# Function Splitting #

@pytest.mark.parametrize(
    "x0", [[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
           [[9, 8, 7], [6, 5, 4], [3, 2, 1]]])
@pytest.mark.parametrize(
    "x1", [[[2, 4, 6], [8, 10, 12], [14, 16, 18]],
           [[18, 16, 14], [12, 10, 8], [6, 4, 2]]])
@pytest.mark.parametrize(
    "chunk_size", [1, 3])
@pytest.mark.parametrize(
    "axis", [0, 1])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_split_func_call(x0, x1, chunk_size, axis, tensor_fn, dev, call):

    # inputs
    in0 = tensor_fn(x0, 'float32', dev)
    in1 = tensor_fn(x1, 'float32', dev)

    # function
    def func(t0, t1):
        return t0 * t1, t0 - t1, t1 - t0

    # predictions
    a, b, c = ivy.split_func_call(func, [in0, in1], 'concat', chunk_size=chunk_size, input_axes=axis)

    # true
    a_true, b_true, c_true = func(in0, in1)

    # value test
    assert np.allclose(ivy.to_numpy(a), ivy.to_numpy(a_true))
    assert np.allclose(ivy.to_numpy(b), ivy.to_numpy(b_true))
    assert np.allclose(ivy.to_numpy(c), ivy.to_numpy(c_true))


@pytest.mark.parametrize(
    "x0", [[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
           [[9, 8, 7], [6, 5, 4], [3, 2, 1]]])
@pytest.mark.parametrize(
    "x1", [[[2, 4, 6], [8, 10, 12], [14, 16, 18]],
           [[18, 16, 14], [12, 10, 8], [6, 4, 2]]])
@pytest.mark.parametrize(
    "chunk_size", [1, 3])
@pytest.mark.parametrize(
    "axis", [0, 1])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_split_func_call_with_cont_input(x0, x1, chunk_size, axis, tensor_fn, dev, call):

    # inputs
    in0 = ivy.Container(cont_key=tensor_fn(x0, 'float32', dev))
    in1 = ivy.Container(cont_key=tensor_fn(x1, 'float32', dev))

    # function
    def func(t0, t1):
        return t0 * t1, t0 - t1, t1 - t0

    # predictions
    a, b, c = ivy.split_func_call(func, [in0, in1], 'concat', chunk_size=chunk_size, input_axes=axis)

    # true
    a_true, b_true, c_true = func(in0, in1)

    # value test
    assert np.allclose(ivy.to_numpy(a.cont_key), ivy.to_numpy(a_true.cont_key))
    assert np.allclose(ivy.to_numpy(b.cont_key), ivy.to_numpy(b_true.cont_key))
    assert np.allclose(ivy.to_numpy(c.cont_key), ivy.to_numpy(c_true.cont_key))


@pytest.mark.parametrize(
    "x", [[0, 1, 2, 3, 4, 5]])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
@pytest.mark.parametrize(
    "devs_as_dict", [True, False])
def test_distribute_array(x, axis, tensor_fn, devs_as_dict, dev, call):

    # inputs
    x = tensor_fn(x, 'float32', dev)

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)
    if devs_as_dict:
        devs = dict(zip(devs, [int((1/len(devs))*x.shape[axis])]*len(devs)))

    # return
    x_split = ivy.dev_dist_array(x, devs, axis)

    # shape test
    assert x_split[dev0].shape[axis] == math.floor(x.shape[axis] / len(devs))

    # value test
    assert min([ivy.dev(x_sub, as_str=True) == ds for ds, x_sub in x_split.items()])


@pytest.mark.parametrize(
    "x", [[0, 1, 2, 3, 4]])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_clone_array(x, axis, tensor_fn, dev, call):

    # inputs
    x = tensor_fn(x, 'float32', dev)

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)

    # return
    x_split = ivy.dev_clone_array(x, devs)

    # shape test
    assert x_split[dev0].shape[0] == math.floor(x.shape[axis] / len(devs))

    # value test
    assert min([ivy.dev(x_sub, as_str=True) == ds for ds, x_sub in x_split.items()])


@pytest.mark.parametrize(
    "xs", [([0, 1, 2], [3, 4])])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_unify_array(xs, axis, tensor_fn, dev, call):

    # devices and inputs
    devs = list()
    dev0 = dev
    x = {dev0: tensor_fn(xs[0], 'float32', dev0)}
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        x[dev1] = tensor_fn(xs[1], 'float32', dev1)
        devs.append(dev1)

    # output
    x_unified = ivy.dev_unify_array(ivy.DevDistItem(x), dev0, 'concat', axis)

    # shape test
    expected_size = 0
    for ds in devs:
        expected_size += x[ds].shape[axis]
    assert x_unified.shape[axis] == expected_size

    # value test
    assert ivy.dev(x_unified, as_str=True) == dev0


@pytest.mark.parametrize(
    "args", [[[0, 1, 2, 3, 4], 'some_str', ([1, 2])]])
@pytest.mark.parametrize(
    "kwargs", [{'a': [0, 1, 2, 3, 4], 'b': 'another_str'}])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_distribute_args(args, kwargs, axis, tensor_fn, dev, call):

    # inputs
    args = [tensor_fn(args[0], 'float32', dev)] + args[1:]
    kwargs = {'a': tensor_fn(kwargs['a'], 'float32', dev), 'b': kwargs['b']}

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)

    # returns
    dist_args, dist_kwargs = ivy.dev_dist_nest(args, kwargs, devs, axis=axis)

    # device specific args
    for ds in devs:
        assert dist_args.at_dev(ds)
        assert dist_kwargs.at_dev(ds)

    # value test
    assert min([ivy.dev(dist_args_ds[0], as_str=True) == ds
                for ds, dist_args_ds in dist_args.at_devs().items()])
    assert min([ivy.dev(dist_kwargs_ds['a'], as_str=True) == ds
                for ds, dist_kwargs_ds in dist_kwargs.at_devs().items()])


@pytest.mark.parametrize(
    "args", [[[0, 1, 2, 3, 4], 'some_str', ([1, 2])]])
@pytest.mark.parametrize(
    "kwargs", [{'a': [0, 1, 2, 3, 4], 'b': 'another_str'}])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_clone_args(args, kwargs, axis, tensor_fn, dev, call):

    # inputs
    args = [tensor_fn(args[0], 'float32', dev)] + args[1:]
    kwargs = {'a': tensor_fn(kwargs['a'], 'float32', dev), 'b': kwargs['b']}

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)

    # returns
    cloned_args, cloned_kwargs = ivy.dev_clone_nest(args, kwargs, devs)

    # device specific args
    for ds in devs:
        assert cloned_args.at_dev(ds)
        assert cloned_kwargs.at_dev(ds)

    # value test
    assert min([ivy.dev(dist_args_ds[0], as_str=True) == ds
                for ds, dist_args_ds in cloned_args.at_devs().items()])
    assert min([ivy.dev(dist_kwargs_ds['a'], as_str=True) == ds
                for ds, dist_kwargs_ds in cloned_kwargs.at_devs().items()])


@pytest.mark.parametrize(
    "args", [[[[0, 1, 2], [3, 4]], 'some_str', ([1, 2])]])
@pytest.mark.parametrize(
    "kwargs", [{'a': [[0, 1, 2], [3, 4]], 'b': 'another_str'}])
@pytest.mark.parametrize(
    "axis", [0])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, helpers.var_fn])
def test_unify_args(args, kwargs, axis, tensor_fn, dev, call):

    # devices
    devs = list()
    dev0 = dev
    devs.append(dev0)
    args_dict = dict()
    args_dict[dev0] = tensor_fn(args[0][0], 'float32', dev0)
    kwargs_dict = dict()
    kwargs_dict[dev0] = tensor_fn(kwargs['a'][0], 'float32', dev0)
    if 'gpu' in dev and ivy.num_gpus() > 1:
        idx = ivy.num_gpus() - 1
        dev1 = dev[:-1] + str(idx)
        devs.append(dev1)
        args_dict[dev1] = tensor_fn(args[0][1], 'float32', dev1)
        kwargs_dict[dev1] = tensor_fn(kwargs['a'][1], 'float32', dev1)

        # inputs
    args = ivy.DevDistNest([ivy.DevDistItem(args_dict)] + args[1:], devs)
    kwargs = ivy.DevDistNest({'a': ivy.DevDistItem(kwargs_dict), 'b': kwargs['b']}, devs)

    # outputs
    args_uni, kwargs_uni = ivy.dev_unify_nest(args, kwargs, dev0, 'concat', axis=axis)

    # shape test
    expected_size_arg = 0
    expected_size_kwarg = 0
    for ds in devs:
        expected_size_arg += args._data[0][ds].shape[axis]
        expected_size_kwarg += kwargs._data['a'][ds].shape[axis]
    assert args_uni[0].shape[axis] == expected_size_arg
    assert kwargs_uni['a'].shape[axis] == expected_size_kwarg

    # value test
    assert ivy.dev(args_uni[0], as_str=True) == dev0
    assert ivy.dev(kwargs_uni['a'], as_str=True) == dev0
