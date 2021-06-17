import pytest


@pytest.fixture(scope="session")
def tl_swap_contract(deploy_contract):
    return deploy_contract("TLSwap")


@pytest.fixture(scope="session")
def tl_currency_network_contract(deploy_contract):
    return deploy_contract("CurrencyNetworkBasic")
