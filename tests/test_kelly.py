import numpy as np
import pytest
from kelly.kelly import kfsingle, kfidouble, expectation, dgsingle, dgidouble

def test_expectation():
    pv = [0.5, 0.5]
    rv = [1, -1]
    assert expectation(pv, rv) == 0
    pv = [0.6, 0.4]
    rv = [2, -1]
    assert np.isclose(expectation(pv, rv), 0.8)

def test_dgsingle():
    pv = [0.5, 0.5]
    rv = [1, -1]
    f = 0.0
    # At f=0, should be the expectation
    assert np.isclose(dgsingle(rv, pv, f), expectation(pv, rv))
    # At f=0.5, should be less than at f=0
    assert dgsingle(rv, pv, 0.5) < dgsingle(rv, pv, 0.0)

def test_dgidouble():
    rv1 = [1, -1]
    rv2 = [2, -2]
    pv1 = [0.5, 0.5]
    pv2 = [0.5, 0.5]
    f1 = 0.0
    f2 = 0.0
    # At f1=f2=0, should be [expectation(rv1, pv1), expectation(rv2, pv2)]
    dg = dgidouble(rv1, rv2, pv1, pv2, f1, f2)
    assert np.allclose(dg, [expectation(pv1, rv1), expectation(pv2, rv2)])

def test_kfsingle_fair_coin():
    # Fair coin, win 1, lose 1, Kelly should be 0
    rv = [1, -1]
    pv = [0.5, 0.5]
    kf = kfsingle(rv, pv)
    assert np.isclose(kf, 0, atol=1e-6)

def test_kfsingle_biased_coin():
    # Biased coin, win 1, lose 1, p(win)=0.6, Kelly should be 0.2
    rv = [1, -1]
    pv = [0.6, 0.4]
    kf = kfsingle(rv, pv)
    assert np.isclose(kf, 0.2, atol=1e-3)

def test_kfidouble_independent():
    # Two independent bets, both with p(win)=0.6, win 1, lose 1
    rv1 = [1, -1]
    rv2 = [1, -1]
    pv1 = [0.6, 0.4]
    pv2 = [0.6, 0.4]
    kf1, kf2 = kfidouble(rv1, rv2, pv1, pv2)
    # Should be close to single Kelly for each
    assert np.isclose(kf1, 0.2, atol=1e-2)
    assert np.isclose(kf2, 0.2, atol=1e-2)