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


def test_tl_swap_emit_initiated_event(
    tl_swap_contract, tl_currency_network_contract, accounts, web3
):
    sender = accounts[1]
    recipient = accounts[2]
    network = tl_currency_network_contract.address
    amount = 100
    tl_swap_contract.functions.commit(
        sender,
        recipient,
        network,
        amount,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact({"from": sender})

    commit_initiated_event = get_single_event_of_contract(
        tl_swap_contract, "Commit", 0,
    )["args"]

    assert commit_initiated_event.hash == HASHED_SECRET
    assert commit_initiated_event.sender == sender
    assert commit_initiated_event.recipient == recipient
    assert commit_initiated_event.TLNetwork == network
    assert commit_initiated_event.TLMoneyAmount == amount
    assert (
        commit_initiated_event.expiryTime
        == WEEK_SECONDS + web3.eth.getBlock("latest").timestamp
    )


def test_tl_swap_commit_entry_alredy_exists(tl_swap_contract):

    tl_swap_contract.functions.commit(
        "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
        "0x94934A417e05091319048701bd4cF61DC48962ac",
        "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
        100,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
    ).transact()

    with pytest.raises(exceptions.TransactionFailed) as excinfo:

        tl_swap_contract.functions.commit(
            "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
            "0x94934A417e05091319048701bd4cF61DC48962ac",
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            200,
            "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
            1,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact()

    assert "Entry already exists" in str(excinfo.value)


def test_tl_swap_commit_tl_money_required(tl_swap_contract):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:

        tl_swap_contract.functions.commit(
            "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
            "0x94934A417e05091319048701bd4cF61DC48962ac",
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            0,
            "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
            1,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact()

    assert "TL total money amount is required" in str(excinfo.value)


def test_tl_swap_commit_eth_address_required(tl_swap_contract):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:
        tl_swap_contract.functions.commit(
            "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
            "0x94934A417e05091319048701bd4cF61DC48962ac",
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            100,
            ZERO_ADDRESS,
            1,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact()

    assert "Ethereum address is required" in str(excinfo.value)


def test_tl_swap_commit_eth_amount_required(tl_swap_contract):
    with pytest.raises(exceptions.TransactionFailed) as excinfo:
        tl_swap_contract.functions.commit(
            "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
            "0x94934A417e05091319048701bd4cF61DC48962ac",
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            100,
            "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
            0,
            WEEK_SECONDS,
            "f81b517a242b218999ec8eec0ea6e2ddbef2a367a14e93f4a32a39e260f686ad",
        ).transact()

    assert "Eth total amount is required" in str(excinfo.value)


def test_tl_swap_claim_tl_money(tl_swap_contract, tl_currency_network_contract):
    tl_swap_contract.functions.commit(
        "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
        "0x94934A417e05091319048701bd4cF61DC48962ac",
        tl_currency_network_contract.address,
        100,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        WEEK_SECONDS,
        HASHED_SECRET,
    ).transact()

    commit_initiated_event = get_single_event_of_contract(
        tl_swap_contract, "Commit", 0,
    )["args"]

    assert commit_initiated_event.hash == HASHED_SECRET
    assert commit_initiated_event.TLMoneyAmount == 100

    extra_data = b""
    tl_swap_contract.functions.claim(
        [
            "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
            "0x94934A417e05091319048701bd4cF61DC48962ac",
        ],
        MAX_FEE,
        extra_data,
        SECRET,
    ).transact()

    currency_transfer_called = get_single_event_of_contract(
        tl_currency_network_contract, "Transfer", 0,
    )["args"]

    assert (
        currency_transfer_called._from == "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e"
    )
    assert currency_transfer_called._to == "0x94934A417e05091319048701bd4cF61DC48962ac"
    assert currency_transfer_called._value == 100
    assert currency_transfer_called._extraData == extra_data


def test_tl_swap_remove_commitment(tl_swap_contract):
    tl_swap_contract.functions.commit(
        "0x9f9f3792287e87d84590E3fe3fD0B34B6E60531e",
        "0x94934A417e05091319048701bd4cF61DC48962ac",
        "0xa6C7310A1fc7A806Fd7c20B4b030501fCe2AC977",
        100,
        "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
        1,
        0,
        HASHED_SECRET,
    ).transact()

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


def test_commit_for_someone_else(
    accounts, tl_currency_network_contract, tl_swap_contract
):
    committer = accounts[0]
    sender = accounts[1]
    recipient = accounts[2]
    network = tl_currency_network_contract.address
    amount = 100
    with pytest.raises(exceptions.TransactionFailed):
        tl_swap_contract.functions.commit(
            sender,
            recipient,
            network,
            amount,
            "0xBf6CA0E4b2B5C788dB424383A95fd019d2EB717f",
            1,
            WEEK_SECONDS,
            HASHED_SECRET,
        ).transact({"from": committer})


def test_claim_your_own_commitment(
    accounts, tl_currency_network_contract, tl_swap_contract
):
    sender = accounts[1]
    recipient = accounts[2]
    network = tl_currency_network_contract.address
    amount = 100

    tl_swap_contract.functions.commit(
        sender,
        recipient,
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

        tl_swap_contract.functions.claim(path, 0, b"", SECRET)
