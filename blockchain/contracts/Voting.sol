// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Privacy-Preserving Voting Smart Contract
 * @author Person 3 (Blockchain & Audit Module)
 * @notice Stores encrypted ballots and enforces nullifier-based double-vote prevention.
 * @dev Contains NO voter personally identifiable information (PII) or plaintext candidate names.
 */
contract Voting {
    address public admin;

    enum ElectionState {
        NOT_STARTED,
        ACTIVE,
        ENDED
    }

    ElectionState public state;
    string public currentElectionId;

    struct VoteRecord {
        string nullifier;
        string encryptedBallot;
        string batchId;
        uint256 timestamp;
        uint256 blockNumber;
    }

    struct BatchInfo {
        string batchId;
        uint256 voteCount;
        uint256 timestamp;
        uint256 blockNumber;
    }

    // Mapping to track used nullifiers per election: electionId => (nullifier => bool)
    mapping(string => mapping(string => bool)) private usedNullifiers;

    // Array of recorded votes
    VoteRecord[] private voteRecords;

    // Mapping for batch details: batchId => BatchInfo
    mapping(string => BatchInfo) private batches;
    string[] private batchIds;

    // Events
    event ElectionStarted(string electionId, uint256 timestamp);
    event ElectionEnded(string electionId, uint256 timestamp);
    event VoteRecorded(
        string indexed electionId,
        string nullifier,
        string batchId,
        uint256 timestamp,
        uint256 blockNumber
    );
    event BatchRecorded(
        string indexed electionId,
        string batchId,
        uint256 count,
        uint256 timestamp
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "Access denied: Caller is not the election admin");
        _;
    }

    modifier electionActive() {
        require(state == ElectionState.ACTIVE, "Election is not active");
        _;
    }

    constructor() {
        admin = msg.sender;
        state = ElectionState.NOT_STARTED;
    }

    /**
     * @notice Starts an election with a specific election ID
     * @param _electionId Unique identifier for the election (e.g., "ELECTION_2026")
     */
    function startElection(string memory _electionId) external onlyAdmin {
        require(bytes(_electionId).length > 0, "Invalid election ID: cannot be empty");
        require(state != ElectionState.ACTIVE, "Election is already active");
        
        currentElectionId = _electionId;
        state = ElectionState.ACTIVE;
        emit ElectionStarted(_electionId, block.timestamp);
    }

    /**
     * @notice Ends the current active election
     */
    function endElection() external onlyAdmin {
        require(state == ElectionState.ACTIVE, "Election is not active");
        
        state = ElectionState.ENDED;
        emit ElectionEnded(currentElectionId, block.timestamp);
    }

    /**
     * @notice Checks if a nullifier has already been recorded for the current election
     * @param _nullifier The nullifier hash to check
     */
    function isNullifierUsed(string memory _nullifier) external view returns (bool) {
        return usedNullifiers[currentElectionId][_nullifier];
    }

    /**
     * @notice Checks if a nullifier has already been recorded for a specific election ID
     * @param _electionId Target election ID
     * @param _nullifier The nullifier hash to check
     */
    function isNullifierUsedForElection(string memory _electionId, string memory _nullifier) external view returns (bool) {
        return usedNullifiers[_electionId][_nullifier];
    }

    /**
     * @notice Records an individual encrypted ballot with nullifier verification
     * @param _nullifier Cryptographic nullifier
     * @param _encryptedBallot Encrypted ballot ciphertext
     * @param _batchId Batch identifier
     */
    function recordVote(
        string memory _nullifier,
        string memory _encryptedBallot,
        string memory _batchId
    ) public onlyAdmin electionActive returns (bool) {
        require(bytes(_nullifier).length > 0, "Invalid nullifier: cannot be empty");
        require(bytes(_encryptedBallot).length > 0, "Invalid encrypted ballot: cannot be empty");
        require(
            !usedNullifiers[currentElectionId][_nullifier],
            "Vote rejected: nullifier has already been used."
        );

        // Mark nullifier as used
        usedNullifiers[currentElectionId][_nullifier] = true;

        // Record vote
        VoteRecord memory newVote = VoteRecord({
            nullifier: _nullifier,
            encryptedBallot: _encryptedBallot,
            batchId: _batchId,
            timestamp: block.timestamp,
            blockNumber: block.number
        });
        voteRecords.push(newVote);

        emit VoteRecorded(currentElectionId, _nullifier, _batchId, block.timestamp, block.number);
        return true;
    }

    /**
     * @notice Records a batch of encrypted ballots atomically
     * @param _batchId Unique batch ID (e.g., "BATCH_001")
     * @param _nullifiers Array of nullifiers in the batch
     * @param _encryptedBallots Array of encrypted ballots corresponding to the nullifiers
     */
    function recordBatch(
        string memory _batchId,
        string[] memory _nullifiers,
        string[] memory _encryptedBallots
    ) external onlyAdmin electionActive returns (uint256) {
        require(_nullifiers.length == _encryptedBallots.length, "Batch size mismatch between nullifiers and ballots");
        require(_nullifiers.length > 0, "Batch cannot be empty");
        require(batches[_batchId].voteCount == 0, "Batch ID already exists");

        for (uint256 i = 0; i < _nullifiers.length; i++) {
            recordVote(_nullifiers[i], _encryptedBallots[i], _batchId);
        }

        batches[_batchId] = BatchInfo({
            batchId: _batchId,
            voteCount: _nullifiers.length,
            timestamp: block.timestamp,
            blockNumber: block.number
        });
        batchIds.push(_batchId);

        emit BatchRecorded(currentElectionId, _batchId, _nullifiers.length, block.timestamp);
        return _nullifiers.length;
    }

    /**
     * @notice Returns total number of recorded votes
     */
    function getVoteCount() external view returns (uint256) {
        return voteRecords.length;
    }

    /**
     * @notice Returns all recorded vote structures
     */
    function getVoteRecords() external view returns (VoteRecord[] memory) {
        return voteRecords;
    }

    /**
     * @notice Returns batch information by batch ID
     * @param _batchId Batch identifier
     */
    function getBatchInformation(string memory _batchId) external view returns (BatchInfo memory) {
        return batches[_batchId];
    }

    /**
     * @notice Returns all recorded batch IDs
     */
    function getAllBatchIds() external view returns (string[] memory) {
        return batchIds;
    }

    /**
     * @notice Returns human-readable election status and current election ID
     */
    function getElectionStatus() external view returns (string memory statusStr, string memory electionId) {
        if (state == ElectionState.NOT_STARTED) {
            statusStr = "NOT_STARTED";
        } else if (state == ElectionState.ACTIVE) {
            statusStr = "ACTIVE";
        } else {
            statusStr = "ENDED";
        }
        electionId = currentElectionId;
    }
}
