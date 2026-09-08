1. System participants

## 1. System Participants

### Person 1 — Identity and Eligibility Authority

Person 1 is responsible for:

- Voter identity verification using iris recognition.
- Checking voter eligibility.
- Maintaining the voter database.
- Checking whether the voter has already voted.
- Providing Person 2 with confirmation that the voter is authenticated and eligible.

Person 1 does not send biometric data to the blockchain.

### Person 2 — Voting and Cryptography Module

Person 2 is responsible for:

- Receiving authorization from Person 1.
- Establishing anonymous voting authorization.
- Generating an election-specific nullifier.
- Encrypting the selected ballot.
- Generating the required cryptographic proof.
- Sending the protected ballot package to Person 3.
- Receiving blockchain confirmation and generating the voting receipt.

### Person 3 — Blockchain Module

Person 3 is responsible for:

- Receiving the protected ballot package from Person 2.
- Verifying the cryptographic proof.
- Checking whether the nullifier has already been used.
- Recording the valid ballot on the blockchain.
- Returning the blockchain transaction hash and confirmation to Person 2.

### Voter

The voter:

- Completes identity verification through Person 1.
- Receives/uses the voting authorization.
- Selects a candidate.
- Participates in the cryptographic voting protocol.

2. Input from Person 1

## 2. Input from Person 1

Person 2 requires an authorization response from Person 1 indicating that the voter has successfully passed identity verification and is eligible to vote.

The identity verification process itself is handled by Person 1 using iris recognition and the voter database.

The conceptual response is:

```json
{
    "authenticated": true,
    "eligible": true
}

3. Authorization mechanism

## 3. Authorization Mechanism

After Person 1 verifies the voter's identity and eligibility, the voter
must receive a cryptographic voting authorization.

The authorization allows an eligible voter to participate in the election
without requiring the voter's identity to be included in the blockchain
transaction.

The authorization should have the following properties:

- It can only be issued to an eligible voter.
- It cannot be forged by an unauthorized person.
- It is valid only for the intended election.
- It should not reveal the voter's identity to Person 3 or the blockchain.
- It should not be reusable for casting multiple votes.
- It should be cryptographically verifiable before the ballot is accepted.

The authorization will be associated with a secret known to the voter.
This secret will later be used to derive an election-specific nullifier.

The authorization process is divided into two boundaries:

1. Identity boundary:
   Person 1 verifies the voter and establishes that the voter is eligible.

2. Anonymous voting boundary:
   Person 2 uses the authorization mechanism to allow the voter to
   participate without exposing the voter's identity to the blockchain.

The exact cryptographic construction used for anonymous authorization
will be defined along with the nullifier and proof mechanisms in the
following sections.

4. Nullifier mechanism

## 4. Nullifier Mechanism

A nullifier is a cryptographic value used to prevent a voter from
casting more than one vote in the same election without revealing the
voter's identity.

The nullifier will be generated using a secret associated with the
voter's anonymous authorization and the election ID.

Conceptually:

    Nullifier = NullifierFunction(VoterSecret, ElectionID)

The nullifier must satisfy the following properties:

- The same voter must produce the same nullifier for the same election.
- The nullifier must be different for different elections.
- The nullifier must not directly reveal the voter's identity.
- A nullifier must be computationally difficult to forge.
- A previously used nullifier must not be accepted again for the same
  election.

Person 3 will maintain a record of used nullifiers. Before recording a
ballot, Person 3 checks whether the submitted nullifier has already been
used.

If the nullifier is already present, the ballot is rejected as a
duplicate vote.

If the nullifier has not been used, the ballot can proceed for
verification and blockchain recording.

Example:

    First submission:
    Nullifier N1 → Not previously used → Accepted

    Second submission:
    Nullifier N1 → Already used → Rejected

The exact cryptographic construction for generating and proving the
nullifier will be finalized as part of the implementation design.

5. Ballot encryption

## 5. Ballot Encryption

The selected candidate must be protected before the ballot is sent to
Person 3. The candidate choice must not be visible to the blockchain
or other unauthorized parties.

Person 2 will use a standard authenticated encryption algorithm to
encrypt the ballot.

The encryption process is:

    Candidate Selection
           ↓
      Ballot Data
           ↓
     AES-GCM Encryption
           ↓
     Encrypted Ballot
           ↓
        Person 3

The ballot will contain only the information required for the election
and voting process. The voter's identity will not be included in the
encrypted ballot.

AES-GCM provides both confidentiality and integrity. Therefore, an
attacker should not be able to read the candidate choice or modify the
encrypted ballot without the modification being detected.

The encryption key must be securely generated and managed. The key
must not be stored together with the encrypted ballot or exposed to
the blockchain.

The encryption/decryption keys and their management will be finalized
in the Key Management section.

The encrypted ballot will be included in the blockchain submission
package sent from Person 2 to Person 3.

6. Proof/verification mechanism

## 6. Proof/Verification Mechanism

Before a ballot is recorded on the blockchain, Person 3 must verify that
the ballot submission is valid.

The proof mechanism is intended to demonstrate that:

- The voter possesses a valid voting authorization.
- The authorization was issued for an eligible voter.
- The submitted nullifier is correctly associated with the authorization
  and the current election.
- The ballot belongs to the intended election.
- The voter has not previously used the same authorization for voting.

The proof should not reveal the voter's identity or the secret associated
with the authorization.

The verification process is:

    Voting Authorization
            +
        Voter Secret
            +
        Election ID
            ↓
       Cryptographic Proof
            ↓
         Person 3
            ↓
       Proof Verification
          /          \
       Valid        Invalid
         ↓             ↓
    Continue         Reject
    voting

7. Output to Person 3

## 7. Output to Person 3

After the voter selects a candidate, Person 2 prepares a protected
ballot package for submission to Person 3.

The ballot package contains only the information required for
cryptographic verification and blockchain recording.

The output from Person 2 to Person 3 is:

```json
{
    "election_id": "E2026",
    "encrypted_ballot": "...",
    "nullifier": "...",
    "proof": "..."
}

8. Blockchain confirmation returned to Person 2

## 8. Blockchain Confirmation Returned to Person 2

After Person 3 verifies the cryptographic proof and nullifier, the valid
ballot is submitted to the blockchain.

Once the blockchain transaction is successfully confirmed, Person 3
returns a confirmation response to Person 2.

The response contains:

```json
{
    "confirmed": true,
    "election_id": "E2026",
    "transaction_hash": "0x..."
}

9. Key management

## 9. Key Management

The cryptographic keys used in the voting system must be generated,
stored, and used securely. Keys must not be stored directly on the
blockchain.

### Types of Keys

The system uses the following cryptographic keys:

1. **Voter Secret**
   - A secret associated with the voter's anonymous voting
     authorization.
   - Used to generate the election-specific nullifier.
   - Must remain confidential and must not be stored on the blockchain.

2. **Election Encryption Key**
   - An election-specific public key is used to protect the ballot.
   - The corresponding private key is kept by the authorized election
     authority for decrypting ballots when required.
   - The private key must never be exposed to Person 3 or stored on the
     blockchain.

3. **Proof/Authorization Keys**
   - Cryptographic keys required for generating and verifying voting
     authorization and proofs.
   - Verification information may be made available to Person 3,
     while secret signing/proving keys remain protected.

### Key Management Requirements

- Keys must be generated using a cryptographically secure random
  number generator.
- Private keys and voter secrets must not be included in blockchain
  transactions.
- Keys must not be hard-coded in the source code.
- Different elections should use different election-specific keys.
- Compromise of one election's key should not automatically compromise
  other elections.
- Key access should be restricted to the component that requires it.
- Key material should be stored securely during implementation, for
  example using protected environment variables or a secure key store.

The blockchain stores only the cryptographic outputs required for
verification and auditing, not private keys or voter secrets.

10. Complete protocol flow

## 10. Complete Protocol Flow

The complete cryptographic voting protocol consists of the following
steps:

### Step 1 — Identity Verification

The voter provides biometric information to Person 1.

Person 1:
- verifies the voter's iris,
- checks voter eligibility,
- checks whether the voter has already voted.

Only an authenticated and eligible voter who has not previously voted
can proceed.

### Step 2 — Voting Authorization

Person 1 establishes that the voter is eligible to vote, after which
an anonymous cryptographic voting authorization is provided to the
voter.

The authorization allows the voter to participate without exposing
their identity to Person 3 or the blockchain.

### Step 3 — Candidate Selection

The voter selects a candidate through the voting interface.

The candidate selection is converted into the required ballot format.

### Step 4 — Ballot Encryption

Person 2 encrypts the ballot using the election's encryption mechanism.

The plaintext candidate selection is not sent to Person 3 or stored on
the blockchain.

### Step 5 — Nullifier Generation

Person 2 generates an election-specific nullifier using the secret
associated with the voting authorization.

The nullifier allows the system to detect reuse of the same voting
authorization without directly revealing the voter's identity.

### Step 6 — Cryptographic Proof Generation

Person 2 generates a proof demonstrating that the ballot was created
using a valid voting authorization and that the nullifier is correctly
associated with that authorization.

The proof does not reveal the voter's identity or biometric information.

### Step 7 — Submission to Person 3

Person 2 sends the following protected package to Person 3:

    Election ID
    Encrypted Ballot
    Nullifier
    Cryptographic Proof

No voter identity or biometric information is included.

### Step 8 — Verification by Person 3

Person 3:

1. Verifies the cryptographic proof.
2. Checks that the election ID is valid.
3. Checks whether the nullifier has already been used.
4. Rejects the ballot if the proof is invalid or the nullifier has
   already been used.
5. Accepts the ballot if all required checks are successful.

### Step 9 — Blockchain Recording

Person 3 submits the valid protected ballot package to the blockchain.

The blockchain records the cryptographic voting data required for
verification and auditing without storing the voter's identity or
plaintext candidate selection.

### Step 10 — Confirmation

After successful blockchain confirmation, Person 3 returns the
transaction hash and confirmation status to Person 2.

Person 2 displays the voting confirmation and transaction hash to the
voter.

### Step 11 — Voter Status Update

Only after successful blockchain confirmation, Person 1 updates the
voter's status to indicate that the voter has completed voting.

### Complete Flow

    Voter
      ↓
    Person 1
    Iris Verification
    Eligibility Check
    Already-Voted Check
      ↓
    Anonymous Voting Authorization
      ↓
    Person 2
    Candidate Selection
      ↓
    Ballot Encryption
      ↓
    Nullifier Generation
      ↓
    Proof Generation
      ↓
    ┌─────────────────────────────┐
    │ Election ID                 │
    │ Encrypted Ballot            │
    │ Nullifier                   │
    │ Cryptographic Proof         │
    └─────────────────────────────┘
      ↓
    Person 3
      ↓
    Proof Verification
    Nullifier Check
      ↓
    Blockchain
      ↓
    Transaction Confirmation
      ↓
    Person 2
      ↓
    Voting Receipt
      ↓
    Person 1
    Update has_voted = TRUE