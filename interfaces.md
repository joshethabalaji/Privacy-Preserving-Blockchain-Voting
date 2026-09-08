# System Interfaces

## 1. Person 1 → Person 2: Authentication and Eligibility

### Success Response

```json
{
    "authenticated": true,
    "eligible": true,
    "has_voted": false
}

### Authentication/Eligibility Failure
```json
{
    "authenticated": false,
    "eligible": false,
    "has_voted": false
}

### Already Voted
```json
{
    "authenticated": true,
    "eligible": true,
    "has_voted": true
}

Person 2 proceeds only when:

authenticated = true
eligible = true
has_voted = false

### 2. Person 2 → Person 1: Anonymous Authorization Request
```json
{
    "election_id": "E2026",
    "blinded_message": "..."
}

### 3. Person 1 → Person 2: Blind Authorization
```json
{
    "election_id": "E2026",
    "blind_signature": "..."
}

### 4. Person 2 → Person 3: Protected Voting Package
```json
{
    "election_id": "E2026",
    "anonymous_public_key": "...",
    "authorization_signature": "...",
    "prepared_message": "...",
    "encrypted_ballot": "...",
    "encrypted_key": "...",
    "nonce": "...",
    "nullifier": "..."
}
The package must not contain:

- Voter ID
- Voter name
- Address
- Iris image
- Fingerprint data
- Raw biometric information
- Plaintext candidate selection

### 5. Person 3: Protected Voting Package Verification

Person 3 verifies:

Required fields are present.
The election ID is valid.
The authorization signature is valid.
The authorization is bound to the election.
The authorization is bound to the anonymous public key.
The nullifier has not already been used.

If the nullifier has already been used:

REJECT

If the nullifier has not been used:

ACCEPT

### 6. Person 3 → Person 2: Blockchain Confirmation
Successful Response
```json
{
    "confirmed": true,
    "election_id": "E2026",
    "transaction_hash": "0x..."
}
Rejected Response
```json
{
    "confirmed": false,
    "election_id": "E2026",
    "transaction_hash": null
}

### 7. Person 3 → Person 1: Vote Confirmation

Person 1 updates has_voted only after successful blockchain
confirmation.

Authentication
      ↓
Eligibility Check
      ↓
Already-voted Check
      ↓
Anonymous Authorization
      ↓
Ballot Encryption
      ↓
Nullifier Generation
      ↓
Person 3 Verification
      ↓
Blockchain Confirmation
      ↓
Person 1 Updates has_voted

### 8. Overall Interface Flow
Person 1
   │
   │ Authentication + Eligibility
   ▼
Person 2
   │
   │ Blinded Authorization Request
   ▼
Person 1
   │
   │ Blind Authorization
   ▼
Person 2
   │
   │ Protected Voting Package
   ▼
Person 3
   │
   │ Blockchain Confirmation
   ▼
Person 2
   │
   ▼
Person 1

### 9. Privacy Boundary
Person 1
Identity + Biometrics + Eligibility
          │
          │
          ▼
Person 2
Anonymous Authorization + Nullifier + Encryption
          │
          │
          ▼
Person 3
Verification + Blockchain Recording

### 10. Security Properties
One-person-one-vote enforcement
Replay resistance
Ballot confidentiality
Ballot integrity
Authorization authenticity
Election separation
Reduced identity-to-ballot linkability
Biometric privacy
Blockchain auditability