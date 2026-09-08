# Person 2 — Security Requirements

## 1. Objective

The objective of Person 2's module is to provide a privacy-preserving voting mechanism that allows an eligible voter to cast a vote without exposing the voter's identity or plaintext vote to the blockchain layer.

Person 2 is responsible for voting authorization, cryptographic protection of the ballot, nullifier generation, and preparation of the ballot for blockchain submission.

## 2. Security Requirements

### 2.1 Eligibility

Only a voter who has been successfully authenticated and verified as eligible by Person 1 can proceed to the voting process.

### 2.2 One-Person-One-Vote

A voter must be able to cast only one valid vote in a particular election.

### 2.3 Vote Confidentiality

The selected candidate must remain confidential. The plaintext candidate choice must not be exposed to the blockchain or unauthorized parties.

### 2.4 Identity Privacy

The blockchain layer must not receive or store personally identifiable voter information such as:

* Voter ID
* Voter name
* Address
* Iris image or biometric information

### 2.5 Voter-Ballot Unlinkability

The blockchain should not be able to determine which real voter is associated with a particular ballot.

### 2.6 Ballot Integrity

Any unauthorized modification of a ballot during transmission or storage must be detectable.

### 2.7 Replay Resistance

A previously used voting authorization or ballot must not be accepted again.

### 2.8 Election Separation

An authorization or nullifier generated for one election must not be reusable in another election.

### 2.9 Authorization Authenticity

Only a legitimately authorized eligible voter should be able to generate a valid voting authorization. An attacker should not be able to forge a valid authorization.

### 2.10 Auditability

A successfully recorded vote should produce verifiable evidence of blockchain submission, such as a transaction hash, without revealing the voter's candidate choice.

## 3. Threat Model

The system considers the following potential attacks:

1. Double voting
2. Authorization/credential replay
3. Forged voting authorization
4. Ballot modification
5. Ballot interception
6. Voter identity leakage
7. Vote/candidate leakage
8. Linking a voter identity to a ballot
9. Submission of an invalid ballot
10. Reuse of an authorization across different elections

## 4. Privacy Boundary

The identity information obtained from Person 1 must remain within the controlled identity/authorization boundary.

Person 2 may temporarily use the voter identity during authorization processing, but the final blockchain payload must not contain the voter's identity.

The blockchain-facing data should contain only the information necessary for vote verification and recording, such as:

* Election ID
* Encrypted ballot
* Nullifier
* Cryptographic proof or authorization evidence

## 5. Expected Data Flow

```text
Person 1
   │
   │ Authenticated + Eligible
   ↓
Person 2
   │
   ├── Voting Authorization
   ├── Nullifier
   ├── Ballot Encryption
   └── Cryptographic Proof
   │
   ↓
Person 3
   │
   │ Encrypted ballot + Nullifier + Proof
   ↓
Blockchain
```

## 6. Success Criteria

The implementation will be considered successful if:

* Only eligible voters can obtain voting authorization.
* A voter cannot successfully vote twice.
* The plaintext candidate is not exposed to the blockchain.
* Voter identity is not included in the blockchain payload.
* Modified ballots are detected.
* Replayed authorizations are rejected.
* Authorizations cannot be reused across elections.
* A valid vote produces blockchain confirmation.
* The system provides evidence that the vote was recorded without revealing the voter's choice.
