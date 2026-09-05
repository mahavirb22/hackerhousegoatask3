// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Verification
 * @dev On-chain registry for verifying facial recognition metadata IPFS records.
 */
contract Verification {
    
    struct Record {
        string ipfsCID;
        address submitter;
        uint256 timestamp;
        bool exists;
    }

    // Mapping from dataHash (bytes32) to Record
    mapping(bytes32 => Record) private _records;

    // Event emitted upon successful recording
    event RecordStored(
        bytes32 indexed dataHash,
        string ipfsCID,
        address indexed submitter,
        uint256 timestamp
    );

    /**
     * @dev Record an IPFS CID associated with a dataHash (bytes32).
     * @param dataHash 32-byte hash computed from facial embedding and post details.
     * @param ipfsCID IPFS CID string pointing to the metadata JSON.
     */
    function record(bytes32 dataHash, string memory ipfsCID) public {
        require(dataHash != bytes32(0), "Verification: dataHash cannot be empty");
        require(bytes(ipfsCID).length > 0, "Verification: ipfsCID cannot be empty");
        require(!_records[dataHash].exists, "Verification: Record already exists for this dataHash");

        _records[dataHash] = Record({
            ipfsCID: ipfsCID,
            submitter: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });

        emit RecordStored(dataHash, ipfsCID, msg.sender, block.timestamp);
    }

    /**
     * @dev Retrieve a recorded record by its dataHash.
     * @param dataHash 32-byte hash identifier.
     */
    function getRecord(bytes32 dataHash) public view returns (
        string memory ipfsCID,
        address submitter,
        uint256 timestamp,
        bool exists
    ) {
        Record memory rec = _records[dataHash];
        return (rec.ipfsCID, rec.submitter, rec.timestamp, rec.exists);
    }
}
