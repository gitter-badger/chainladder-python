import numpy as np
import pytest
from numpy.testing import assert_allclose
import chainladder as cl
from rpy2.robjects.packages import importr
from rpy2.robjects import r

CL = importr('ChainLadder')


@pytest.fixture
def atol():
    return 1e-5


def mack_r(data, alpha, est_sigma, tail):
    if tail:
        return r(f'mack<-MackChainLadder({data},alpha={alpha}, est.sigma="{est_sigma}", tail=TRUE)')
    else:
        return r(f'mack<-MackChainLadder({data},alpha={alpha}, est.sigma="{est_sigma}")')


def mack_p(data, average, est_sigma, tail):
    if tail:
        return cl.MackChainladder().fit(cl.TailCurve(curve='exponential').fit_transform(cl.Development(average=average, sigma_interpolation=est_sigma).fit_transform(cl.load_dataset(data))))
    else:
        return cl.MackChainladder().fit(cl.Development(average=average, sigma_interpolation=est_sigma).fit_transform(cl.load_dataset(data)))


data = ['RAA', 'ABC', 'GenIns', 'MW2008', 'MW2014']
tail = [True, False]
averages = [('simple', 2), ('volume', 1), ('regression', 0)]
est_sigma = [('log-linear', 'log-linear'), ('mack', 'Mack')]


def test_mack_to_triangle():
    assert cl.MackChainladder().fit(cl.TailConstant().fit_transform(cl.Development().fit_transform(cl.load_dataset('ABC')))).summary_ == \
        cl.MackChainladder().fit(cl.Development().fit_transform(cl.load_dataset('ABC'))).summary_


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_full_std_err(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('F.se')
    p = mack_p(data, averages[0], est_sigma[0], tail).full_std_err_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.array(df[0])
    assert_allclose(r, p, atol=atol)


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_process_risk(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('Mack.ProcessRisk')
    p = mack_p(data, averages[0], est_sigma[0], tail).process_risk_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.array(df[0])
    assert_allclose(r, p, atol=atol)


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_parameter_risk(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('Mack.ParameterRisk')
    p = mack_p(data, averages[0], est_sigma[0], tail).parameter_risk_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.array(df[0])
    assert_allclose(r, p, atol=atol)


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_total_process_risk(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('Total.ProcessRisk')
    p = mack_p(data, averages[0], est_sigma[0], tail).total_process_risk_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.expand_dims(np.array(df[0]), 0)
    assert_allclose(r, p, atol=atol)


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_total_parameter_risk(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('Total.ParameterRisk')
    p = mack_p(data, averages[0], est_sigma[0], tail).total_parameter_risk_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.expand_dims(np.array(df[0]),0)
    assert_allclose(r, p, atol=atol)


@pytest.mark.parametrize('data', data)
@pytest.mark.parametrize('averages', averages)
@pytest.mark.parametrize('est_sigma', est_sigma)
@pytest.mark.parametrize('tail', tail)
def test_mack_mack_std_err_(data, averages, est_sigma, tail, atol):
    df = mack_r(data, averages[1], est_sigma[1], tail).rx('Mack.S.E')
    p = mack_p(data, averages[0], est_sigma[0], tail).mack_std_err_.triangle[0, 0, :, :]
    p = p[:, :-1] if not tail else p
    r = np.array(df[0])
    assert_allclose(r, p, atol=atol)
