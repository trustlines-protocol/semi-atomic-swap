import pytest
from eth_abi import encode_single
from eth_tester import exceptions
from web3 import Web3

ZERO_ADDRESS = "0x" + "0" * 40

SECRET = encode_single("bytes32", b"123456ab")
HASHED_SECRET = Web3.solidityKeccak(["bytes32"], [SECRET])
MAX_FEE = 2 ** 64 - 1
WEEK_SECONDS = 60 * 60 * 24 * 7


def get_events_of_contract(contract, event_name, from_block=0):
    return list(getattr(contract.events, event_name).getLogs(fromBlock=from_block))


def get_single_event_of_contract(contract, event_name, from_block=0):
    events = get_events_of_contract(contract, event_name, from_block)
    assert len(events) == 1, f"No single event of type {event_name}"
    return events[0]


@pytest.fixture()
def sender(accounts):
    return accounts[1]


@pytest.fixture()
def receiver(accounts):
    return accounts[2]


@pytest.fixture()
def swap_tl_amount():
    return 100


@pytest.fixture()
def commit_swap(
    tl_swap_contract, tl_currency_network_contract, sender, receiver, swap_tl_amount
):
    tl_swap_contract.functions.commit(
        receiver,
        tl_currency_network_contract.address,
        swap_tl_amount,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact({"from": sender})


def test_tl_swap_emit_initiated_event(
    tl_swap_contract, tl_currency_network_contract, accounts, web3
):
    sender = accounts[1]
    receiver = accounts[2]
    network = tl_currency_network_contract.address
    amount = 100
    tl_swap_contract.functions.commit(
        receiver, network, amount, receiver, 1, WEEK_SECONDS, HASHED_SECRET,
    ).transact({"from": sender})

    commit_initiated_event = get_single_event_of_contract(
        tl_swap_contract, "Commit", 0,
    )["args"]

    assert commit_initiated_event.hash == HASHED_SECRET
    assert commit_initiated_event.sender == sender
    assert commit_initiated_event.receiver == receiver
    assert commit_initiated_event.TLNetwork == network
    assert commit_initiated_event.TLMoneyAmount == amount
    assert (
        commit_initiated_event.expiryTime
        == WEEK_SECONDS + web3.eth.getBlock("latest").timestamp
    )


def test_tl_swap_commit_entry_alredy_exists(
    tl_swap_contract, tl_currency_network_contract, sender, receiver
):

    tl_swap_contract.functions.commit(
        receiver,
        tl_currency_network_contract.address,
        100,
        receiver,
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact({"from": sender})

    with pytest.raises(exceptions.TransactionFailed) as excinfo:

        tl_swap_contract.functions.commit(
            receiver,
            tl_currency_network_contract.address,
            200,
            receiver,
            1,
            WEEK_SECONDS,
            HASHED_SECRET,
        ).transact({"from": sender})

    assert "Entry already exists" in str(excinfo.value)


def test_tl_swap_commit_tl_money_required(
    tl_swap_contract, sender, receiver, tl_currency_network_contract
):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:

        tl_swap_contract.functions.commit(
            receiver,
            tl_currency_network_contract.address,
            0,
            "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
            1,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact({"from": sender})

    assert "TL total money amount is required" in str(excinfo.value)


def test_tl_swap_commit_eth_address_required(
    tl_swap_contract, sender, receiver, tl_currency_network_contract
):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:
        tl_swap_contract.functions.commit(
            receiver,
            tl_currency_network_contract.address,
            100,
            ZERO_ADDRESS,
            1,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact({"from": sender})

    assert "Ethereum address is required" in str(excinfo.value)


def test_tl_swap_commit_eth_amount_required(
    tl_swap_contract, sender, receiver, tl_currency_network_contract
):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:
        tl_swap_contract.functions.commit(
            receiver,
            tl_currency_network_contract.address,
            100,
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            0,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact({"from": sender})

    assert "Eth total amount is required" in str(excinfo.value)


def test_tl_swap_claim_tl_money(
    tl_swap_contract, tl_currency_network_contract, sender, receiver
):
    tl_swap_contract.functions.commit(
        receiver,
        tl_currency_network_contract.address,
        100,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact({"from": sender})

    extra_data = b""
    tl_swap_contract.functions.claim(
        [sender, receiver], MAX_FEE, extra_data, SECRET,
    ).transact({"from": receiver})

    currency_transfer_called = get_single_event_of_contract(
        tl_currency_network_contract, "Transfer", 0,
    )["args"]

    assert currency_transfer_called._from == sender
    assert currency_transfer_called._to == receiver
    assert currency_transfer_called._value == 100
    assert currency_transfer_called._extraData == extra_data


def test_tl_swap_remove_commitment(
    tl_swap_contract, tl_currency_network_contract, sender, receiver
):
    tl_swap_contract.functions.commit(
        receiver,
        tl_currency_network_contract.address,
        100,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        0,
        HASHED_SECRET,
    ).transact({"from": sender})

    commit_initiated_event = get_single_event_of_contract(
        tl_swap_contract, "Commit", 0,
    )["args"]

    assert commit_initiated_event.hash == HASHED_SECRET
    assert commit_initiated_event.TLMoneyAmount == 100

    tl_swap_contract.functions.removeCommitment(HASHED_SECRET).transact()

    expired_event = get_single_event_of_contract(
        tl_swap_contract, "ExpireCommitment", 0,
    )["args"]

    assert expired_event.hash == HASHED_SECRET


@pytest.mark.usefixtures("commit_swap")
def test_claim_removed_commitment(tl_swap_contract, chain, sender, receiver, web3):
    expiry_time = web3.eth.getBlock("latest").timestamp + WEEK_SECONDS + 1
    chain.time_travel(expiry_time)
    tl_swap_contract.functions.removeCommitment(HASHED_SECRET).transact()
    with pytest.raises(exceptions.TransactionFailed):
        tl_swap_contract.functions.claim(
            [sender, receiver], MAX_FEE, b"", SECRET,
        ).transact()


def test_claim_your_own_commitment(
    accounts, tl_currency_network_contract, tl_swap_contract, sender, receiver
):
    network = tl_currency_network_contract.address
    amount = 100

    tl_swap_contract.functions.commit(
        receiver,
        network,
        amount,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact({"from": sender})

    with pytest.raises(exceptions.TransactionFailed):
        sender_friend = accounts[3]
        path = [sender, sender_friend, sender]

        tl_swap_contract.functions.claim(path, 0, b"", SECRET).transact(
            {"from": receiver}
        )
