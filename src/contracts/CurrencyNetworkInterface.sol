pragma solidity ^0.8.3;

/**
 * @title Interface with function for transferFrom of currency network
 **/
interface CurrencyNetworkInterface {

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
    ) external;
}

// SPDX-License-Identifier: MIT
