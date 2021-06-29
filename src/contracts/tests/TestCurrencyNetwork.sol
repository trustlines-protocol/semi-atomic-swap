pragma solidity ^0.8.3;

/**
 * @title Test contract representing a currency network
 * Has a mock transferFrom function that will just emit an event.
 **/
contract TestCurrencyNetwork {

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
