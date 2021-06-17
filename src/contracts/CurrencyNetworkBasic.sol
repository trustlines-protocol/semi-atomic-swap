pragma solidity ^0.8.3;

/**
 * @title Basic functionalities of Currency Networks
 * @notice Main contract of Trustlines, encapsulates all trustlines of one currency network.
 * Implements core features of currency networks related to opening / closing trustline and transfers.
 * Also includes freezing of TL / currency networks, interests and fees.
 **/
contract CurrencyNetworkBasic {

    event Transfer(
        address indexed _from,
        address indexed _to,
        uint256 _value,
        bytes _extraData
    );

    /**
     * @notice send `_value` along `_path`
     * msg.sender needs to be authorized to call this function
     * @param _value The amount of token to be transferred
     * @param _maxFee Maximum fee the sender wants to pay
     * @param _path Path of transfer starting with sender and ending with receiver
     * @param _extraData extra data bytes to be logged in the Transfer event
     **/
    function transferFrom(
        uint64 _value,
        uint64 _maxFee,
        address[] calldata _path,
        bytes calldata _extraData
    ) external {
        emit Transfer(_path[0], _path[_path.length - 1], _value, _extraData);
    }
}

// SPDX-License-Identifier: MIT
