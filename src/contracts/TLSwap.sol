pragma solidity 0.8.3;

import "./CurrencyNetworkInterface.sol";

contract TLSwap {

    CurrencyNetworkInterface _currency;

    struct Commitment {
        address payable initiator;
        address payable recipient;
        address TLNetwork;
        uint64 TLMoneyAmount;
        uint64 endTimeStamp;
        address initiatorEthAddress;
        uint256 EthAmount;
    }

    mapping(bytes32 => Commitment) public CommitmentsMap; // the key is the hash

    event Commit(bytes32 indexed hash, address sender, address receiver, address TLNetwork, uint256 TLMoneyAmount, uint64 expiryTime);
    event Claim(bytes32 indexed hash, address sender, address receiver, address TLNetwork, uint256 TLMoneyAmount);
    event ExpireCommitment(bytes32 indexed hash);

    function commit(address payable _TLRecipient, address _TLNetwork,
        uint64 _TLMoneyAmount,
        address _InitiatorEthAddress,
        uint _EthAmount,
        uint64 _lockTimeSec, bytes32 _hash) external {

        require(CommitmentsMap[_hash].initiator == address(0x0), "Entry already exists");
        require(_TLMoneyAmount > 0, "TL total money amount is required");
        require(_InitiatorEthAddress != address(0x0), "Ethereum address is required");
        require(_EthAmount > 0, "Eth total amount is required");

        uint64 expiryTime = uint64(block.timestamp + _lockTimeSec);

        CommitmentsMap[_hash].initiator = payable(msg.sender);
        CommitmentsMap[_hash].recipient = _TLRecipient;
        CommitmentsMap[_hash].endTimeStamp = expiryTime;
        CommitmentsMap[_hash].TLMoneyAmount = _TLMoneyAmount;
        CommitmentsMap[_hash].TLNetwork =_TLNetwork;
        CommitmentsMap[_hash].initiatorEthAddress = _InitiatorEthAddress;
        CommitmentsMap[_hash].EthAmount = _EthAmount;

        emit Commit(_hash, msg.sender, _TLRecipient, _TLNetwork, _TLMoneyAmount, expiryTime);
    }


    function claim(address[] calldata _path,
        uint64 _maxFee,
        bytes calldata _extraData,
        bytes32 _proof) external {

        bytes32 hash = keccak256(abi.encodePacked(_proof));
        require(CommitmentsMap[hash].initiator != address(0x0), "No entry found");
        require(CommitmentsMap[hash].endTimeStamp >= block.timestamp, "TimeStamp violation");
        require(CommitmentsMap[hash].recipient == msg.sender, "Claim msg sender must be recipient");
        require(CommitmentsMap[hash].initiator == _path[0], "Path must start with commitment sender");
        require(CommitmentsMap[hash].recipient == _path[_path.length - 1], "Path must end with commitment recipient");

        address networkAddress = CommitmentsMap[hash].TLNetwork;
        uint64 TlMoneyAmount = CommitmentsMap[hash].TLMoneyAmount;

        delete CommitmentsMap[hash];

        _currency = CurrencyNetworkInterface(networkAddress);
        _currency.transferFrom(TlMoneyAmount, _maxFee, _path, _extraData);

        emit Claim(hash, _path[0], _path[_path.length - 1], networkAddress, TlMoneyAmount);
    }

    /*
     * We currently just remove the commitment. In the future we could
     * make sure that if a transfer didn't succeed we could add a dept
     * in the currency network
     */
    function removeCommitment(bytes32 _hash) external {
        require(CommitmentsMap[_hash].initiator != address(0x0), "No entry found");
        require(CommitmentsMap[_hash].endTimeStamp < block.timestamp, "TimeStamp violation");

        delete CommitmentsMap[_hash];

        emit ExpireCommitment(_hash);
    }
}


// SPDX-License-Identifier: MIT
