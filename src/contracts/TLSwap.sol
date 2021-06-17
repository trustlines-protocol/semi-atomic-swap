pragma solidity 0.8.3;

import "./CurrencyNetworkBasic.sol";

contract TLSwap {

    CurrencyNetworkBasic _currency;

    struct Commitment {
        address payable initiator;
        uint64 endTimeStamp;
        address payable recipient;
        uint64 TLMoneyAmount;
        address TLNetwork;
        address initiatorEthAddress;
        uint256 EthAmount;
    }

    mapping(bytes32 => Commitment) public CommitmentsMap; // the key is the hash

    event CommitmentInitiatedEvent(bytes32 indexed hash, uint256 TLMoneyAmount);
    event CommitmentSuccessEvent(bytes32 indexed hash, uint256 TLMoneyAmount, address TLNetwork, address initiatorEthAddress, uint EthAmount);
    event CommitmentExpiredEvent(bytes32 indexed hash);

    function commit(address payable _TLSender, address payable _TLRecipient, address _TLNetwork,
        uint64 _TLMoneyAmount,
        address _InitiatorEthAddress,
        uint _EthAmount,
        uint64 _lockTimeSec, bytes32 _hash) external payable {

        require(CommitmentsMap[_hash].initiator == address(0x0), "Entry already exists");
        require(_TLMoneyAmount > 0, "TL total money amount is required");
        require(_InitiatorEthAddress != address(0x0), "Ethereum address is required");
        require(_EthAmount > 0, "Eth total amount is required");

        CommitmentsMap[_hash].initiator = _TLSender;
        CommitmentsMap[_hash].recipient = _TLRecipient;
        CommitmentsMap[_hash].endTimeStamp = uint64(block.timestamp + _lockTimeSec);
        CommitmentsMap[_hash].TLMoneyAmount = _TLMoneyAmount;
        CommitmentsMap[_hash].TLNetwork =_TLNetwork;
        CommitmentsMap[_hash].initiatorEthAddress = _InitiatorEthAddress;
        CommitmentsMap[_hash].EthAmount = _EthAmount;

        emit CommitmentInitiatedEvent(_hash, _TLMoneyAmount);
    }


    function claim(address[] calldata _path,
        uint64 _maxFee,
        bytes calldata _extraData,
        bytes32 _proof) external {
        bytes32 hash = keccak256(abi.encodePacked(_proof));

        address networkAddress = CommitmentsMap[hash].TLNetwork;
        uint64 TlMoneyAmount = CommitmentsMap[hash].TLMoneyAmount;

        require(CommitmentsMap[hash].initiator != address(0x0), "No entry found");
        require(CommitmentsMap[hash].endTimeStamp >= block.timestamp, "TimeStamp violation");

        clean(hash);

        _currency = CurrencyNetworkBasic(networkAddress);
        _currency.transferFrom(TlMoneyAmount, _maxFee, _path, _extraData);
    }

    /*
     * We currently just remove the commitment. In the future we could
     * make sure that if a transfer didn't succeed we could add a dept
     * in the currency network
     */
    function removeCommitment(bytes32 _hash) external {
        require(CommitmentsMap[_hash].initiator != address(0x0), "No entry found");
        require(CommitmentsMap[_hash].endTimeStamp < block.timestamp, "TimeStamp violation");

        clean(_hash);

        emit CommitmentExpiredEvent(_hash);
    }

    function clean(bytes32 _hash) private {
        Commitment storage commitment = CommitmentsMap[_hash];

        delete commitment.initiator;
        delete commitment.recipient;
        delete commitment.endTimeStamp;
        delete commitment.TLMoneyAmount;
        delete commitment.TLNetwork;
        delete commitment.initiatorEthAddress;
        delete commitment.EthAmount;

        delete CommitmentsMap[_hash];
    }
}


// SPDX-License-Identifier: MIT
