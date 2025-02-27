# Copyright 2019-2021 ETH Zurich and the DaCe authors. All rights reserved.
""" Tests automatic detection and baking of callbacks in the Python frontend. """
import dace
import numpy as np
import pytest
import time
from dace import config

N = dace.symbol('N')


def dace_inhibitor(f):
    return f


@dace_inhibitor
def almost_gemm(A, alpha, B):
    return alpha * A @ B


@dace_inhibitor
def almost_gemm_2(A, alpha, B):
    return alpha * A @ B, alpha * np.float64(2)


@dace_inhibitor
def scale(C, beta):
    C *= beta


def test_automatic_callback():
    @dace.program
    def autocallback(A: dace.float64[N, N], B: dace.float64[N, N], C: dace.float64[N, N], beta: dace.float64):
        tmp: dace.float64[N, N] = almost_gemm(A, 0.5, B)
        scale(C, beta)
        C += tmp

    A = np.random.rand(24, 24)
    B = np.random.rand(24, 24)
    C = np.random.rand(24, 24)
    beta = np.float64(np.random.rand())
    expected = 0.5 * A @ B + beta * C

    autocallback(A, B, C, beta)

    assert np.allclose(C, expected)


def test_automatic_callback_2():
    @dace.program
    def autocallback(A: dace.float64[N, N], B: dace.float64[N, N], C: dace.float64[N, N], beta: dace.float64):
        tmp: dace.float64[N, N]
        tmp2: dace.float64
        tmp, tmp2 = almost_gemm_2(A, 0.5, B)
        scale(C, beta)
        C += tmp * tmp2

    A = np.random.rand(24, 24)
    B = np.random.rand(24, 24)
    C = np.random.rand(24, 24)
    beta = np.float64(np.random.rand())
    expected = 0.5 * A @ B * 0.5 * 2 + beta * C

    autocallback(A, B, C, beta)

    assert np.allclose(C, expected)


def test_automatic_callback_inference():
    @dace.program
    def autocallback_ret(A: dace.float64[N, N], B: dace.float64[N, N], C: dace.float64[N, N], beta: dace.float64):
        tmp = np.ndarray([N, N], dace.float64)
        tmp[:] = almost_gemm(A, 0.5, B)
        scale(C, beta)
        C += tmp

    A = np.random.rand(24, 24)
    B = np.random.rand(24, 24)
    C = np.random.rand(24, 24)
    beta = np.float64(np.random.rand())
    expected = 0.5 * A @ B + beta * C

    autocallback_ret(A, B, C, beta)

    assert np.allclose(C, expected)


def test_automatic_callback_inference_2():
    @dace.program
    def autocallback_ret(A: dace.float64[N, N], B: dace.float64[N, N], C: dace.float64[N, N], beta: dace.float64):
        tmp = np.ndarray([N, N], dace.float64)
        tmp2 = np.float64(0.0)
        tmp[:], tmp2 = almost_gemm_2(A, 0.5, B)
        scale(C, beta)
        C += tmp * tmp2

    A = np.random.rand(24, 24)
    B = np.random.rand(24, 24)
    C = np.random.rand(24, 24)
    beta = np.float64(np.random.rand())
    expected = 0.5 * A @ B * 0.5 * 2 + beta * C

    autocallback_ret(A, B, C, beta)

    assert np.allclose(C, expected)


def test_automatic_callback_method():
    class NotDace:
        def __init__(self):
            self.q = np.random.rand()

        @dace_inhibitor
        def method(self, a):
            return a * self.q

    nd = NotDace()

    @dace.program
    def autocallback_method(A: dace.float64[N, N]):
        tmp: dace.float64[N, N] = nd.method(A)
        return tmp

    A = np.random.rand(24, 24)

    out = autocallback_method(A)

    assert np.allclose(out, nd.q * A)


@dace.program
def modcallback(A: dace.float64[N, N], B: dace.float64[N]):
    tmp: dace.float64[N] = np.median(A, axis=1)
    B[:] = tmp


def test_callback_from_module():
    N.set(24)
    A = np.random.rand(24, 24)
    B = np.random.rand(24)
    modcallback(A, B)
    diff = np.linalg.norm(B - np.median(A, axis=1))
    print('Difference:', diff)
    assert diff <= 1e-5


def sq(a):
    return a * a


@dace.program
def tasklet_callback(A: dace.float64[N, N], B: dace.float64[N, N]):
    for i, j in dace.map[0:N, 0:N]:
        with dace.tasklet:
            a << A[i, j]
            b >> B[i, j]
            b = sq(a)


@pytest.mark.skip
def test_callback_tasklet():
    A = np.random.rand(24, 24)
    B = np.random.rand(24, 24)
    tasklet_callback(A, B)
    assert np.allclose(A * A, B)


def test_view_callback():
    @dace.program
    def autocallback(A: dace.float64[2 * N, N], B: dace.float64[N, N], C: dace.float64[N, N], beta: dace.float64):
        A[N:, :] = almost_gemm(A[:N, :], 0.5, B)
        scale(C, beta)
        C += A[N:, :]

    A = np.random.rand(48, 24)
    B = np.random.rand(24, 24)
    C = np.random.rand(24, 24)
    beta = np.float64(np.random.rand())
    expected = 0.5 * A[:24] @ B + beta * C

    autocallback(A, B, C, beta)

    assert np.allclose(C, expected)


def test_print():
    @dace.program
    def printprog(a: dace.float64[2, 2]):
        print(a, 'hello')

    a = np.random.rand(2, 2)
    printprog(a)


def test_reorder():
    counter = 0
    should_be_one, should_be_two = 0, 0

    @dace_inhibitor
    def a():
        nonlocal counter
        nonlocal should_be_two
        counter += 1
        should_be_two = counter

    @dace_inhibitor
    def b():
        nonlocal counter
        nonlocal should_be_one
        counter += 1
        should_be_one = counter

    @dace.program
    def do_not_reorder():
        b()
        a()

    sdfg = do_not_reorder.to_sdfg()
    assert list(sdfg.arrays.keys()) == ['__pystate']

    do_not_reorder()
    assert should_be_one == 1
    assert should_be_two == 2


def test_reorder_nested():
    counter = 0
    should_be_one, should_be_two = 0, 0

    @dace_inhibitor
    def a():
        nonlocal counter
        nonlocal should_be_two
        counter += 1
        should_be_two = counter

    def call_a():
        a()

    @dace_inhibitor
    def b():
        nonlocal counter
        nonlocal should_be_one
        counter += 1
        should_be_one = counter

    @dace.program
    def call_b():
        b()

    @dace.program
    def do_not_reorder_nested():
        call_b()
        call_a()

    sdfg = do_not_reorder_nested.to_sdfg()
    assert list(sdfg.arrays.keys()) == ['__pystate']

    do_not_reorder_nested()
    assert should_be_one == 1
    assert should_be_two == 2


def test_callback_samename():
    counter = 0
    should_be_one, should_be_two = 0, 0

    def get_func_a():
        @dace_inhibitor
        def b():
            nonlocal counter
            nonlocal should_be_two
            counter += 1
            should_be_two = counter

        def call_a():
            b()

        return call_a

    def get_func_b():
        @dace_inhibitor
        def b():
            nonlocal counter
            nonlocal should_be_one
            counter += 1
            should_be_one = counter

        @dace.program
        def call_b():
            b()

        return call_b

    call_a = get_func_a()
    call_b = get_func_b()

    @dace.program
    def same_name_nested():
        call_b()
        call_a()

    sdfg = same_name_nested.to_sdfg(simplify=False)
    assert list(sdfg.arrays.keys()) == ['__pystate']

    same_name_nested()
    assert should_be_one == 1
    assert should_be_two == 2


# Cannot run test without cupy
@pytest.mark.skip
def test_gpu_callback():
    import cupy as cp

    @dace_inhibitor
    def cb_with_gpu(arr):
        assert isinstance(arr, cp.ndarray)
        arr *= 2

    @dace.program
    def gpucallback(A):
        tmp = dace.ndarray([20], dace.float64, storage=dace.StorageType.GPU_Global)
        tmp[:] = A
        cb_with_gpu(tmp)
        A[:] = tmp

    a = cp.random.rand(20)
    expected = a * 2
    gpucallback(a)

    assert cp.allclose(a, expected)


def test_bad_closure():
    """ 
    Testing functions that should not be in the closure (must be implemented as
    callbacks).
    """
    @dace.program
    def timeprog(A: dace.float64[20]):
        # Library function that does not return the same value every time
        A[:] = time.time()

    A = np.random.rand(20)
    B = np.random.rand(20)
    now = time.time()
    timeprog(A)
    timeprog(B)

    assert np.all(B > A) and np.all(A > now)


def test_object_with_nested_callback():
    c = np.random.rand(20)

    @dace_inhibitor
    def call_another_function(a, b):
        nonlocal c
        c[:] = a + b

    class MyObject:
        def __call__(self, a, b):
            c = dict(a=a, b=b)
            call_another_function(**c)

    obj = MyObject()

    @dace.program
    def callobj(a, b):
        obj(a, b)

    a = np.random.rand(20)
    b = np.random.rand(20)
    callobj(a, b)
    assert np.allclose(c, a + b)


def test_two_parameters_same_name():
    @dace_inhibitor
    def add(a, b):
        return a + b

    @dace.program
    def calladd(A: dace.float64[20], B: dace.float64[20]):
        B[:] = add(A, A)

    a = np.random.rand(20)
    b = np.random.rand(20)
    calladd(a, b)
    assert np.allclose(b, a + a)


def test_inout_same_name():
    @dace_inhibitor
    def add(a, b):
        return a + b

    @dace.program
    def calladd(A: dace.float64[20]):
        A[:] = add(A, A)

    a = np.random.rand(20)
    expected = a + a
    calladd(a)
    assert np.allclose(expected, a)


def test_inhibit_state_fusion():
    """ Tests that state fusion is inhibited around callbacks if configured as such. """
    @dace_inhibitor
    def add(a, b):
        return a + b

    @dace.program
    def calladd(A: dace.float64[20], B: dace.float64[20], C: dace.float64[20], D: dace.float64[20]):
        A[:] = add(B, C)
        D[:] = add(A, C)

    with config.set_temporary('frontend', 'dont_fuse_callbacks', value=True):
        sdfg = calladd.to_sdfg(simplify=True)
        assert sdfg.number_of_nodes() == 5

    with config.set_temporary('frontend', 'dont_fuse_callbacks', value=False):
        sdfg = calladd.to_sdfg(simplify=True)
        assert sdfg.number_of_nodes() == 1


def test_two_callbacks():
    called_cnt = 0

    @dace_inhibitor
    def call(arr):
        nonlocal called_cnt
        called_cnt += 1

    @dace.program
    def call_twice(arr, scal):
        call(arr)
        arr[:] = arr[:] * scal
        call(arr)

    arr = np.ones((12, ), np.float64)
    scal = 2

    call_twice(arr, scal)
    assert called_cnt == 2


def test_two_callbacks_different_sig():
    called_cnt = 0

    @dace_inhibitor
    def call(*args):
        nonlocal called_cnt
        called_cnt += 1

    @dace.program
    def call_twice(arr, scal):
        call()
        arr[:] = arr[:] * scal
        call(arr)

    @dace.program
    def call_twice_2(arr, scal):
        call_twice(arr, scal)

    arr = np.ones((12, ), np.float64)
    scal = 2

    call_twice_2(arr, scal)
    assert called_cnt == 2


def test_two_callbacks_different_type():
    called_cnt = 0

    @dace_inhibitor
    def call(array):
        nonlocal called_cnt
        called_cnt += 1

    @dace.program
    def call_twice(arr: dace.float64[20], arr2: dace.int32[20, 20]):
        call(arr)
        arr *= arr2[1]
        call(arr2)

    @dace.program
    def call_twice_3(arr: dace.float64[20], arr2: dace.int32[20, 20]):
        call_twice(arr, arr2)

    arr = np.ones((20, ), np.float64)
    arr2 = np.full((20, 20), 2, np.int32)

    call_twice_3(arr, arr2)
    assert called_cnt == 2


def test_disallowed_keyword():
    class Obj:
        def hello(a):
            try:
                return a + 1
            except:
                return a + 2

    @dace
    def prog(a: dace.float64[10]):
        b: dace.float64[10] = Obj.hello(a)
        return b

    a = np.random.rand(10)
    assert np.allclose(prog(a), a + 1)


def test_nested_duplicate_callbacks():
    called = 0

    @dace_inhibitor
    def callback(*args):
        nonlocal called
        called += len(args)

    @dace.program
    def myprogram_1(a):
        callback(a[0])
        for i in range(a.shape[0]):
            a[i] += i
        callback(a[0], a[1])
        return np.sum(a)

    @dace.program
    def myprogram(a):
        myprogram_1(a)

    a = np.random.rand(20, 1)
    sdfg = myprogram.to_sdfg(a)
    build_folder = sdfg.build_folder

    myprogram(a)
    # Ensure the cache is clear
    myprogram._cache.clear()

    myprogram.load_precompiled_sdfg(build_folder, a)
    assert len(myprogram._cache.cache) == 1

    myprogram(a)
    assert called == 6


if __name__ == '__main__':
    test_automatic_callback()
    test_automatic_callback_2()
    test_automatic_callback_inference()
    test_automatic_callback_inference_2()
    test_automatic_callback_method()
    test_callback_from_module()
    test_view_callback()
    # test_callback_tasklet()
    test_print()
    test_reorder()
    test_reorder_nested()
    test_callback_samename()
    # test_gpu_callback()
    test_bad_closure()
    test_object_with_nested_callback()
    test_two_parameters_same_name()
    test_inout_same_name()
    test_inhibit_state_fusion()
    test_two_callbacks()
    test_two_callbacks_different_sig()
    test_two_callbacks_different_type()
    test_disallowed_keyword()
    test_nested_duplicate_callbacks()
