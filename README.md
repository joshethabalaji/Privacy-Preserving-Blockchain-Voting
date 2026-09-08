# Privacy-Preserving Blockchain Voting System

## Overview

This project presents a privacy-preserving electronic voting system that combines **biometric voter verification, cryptographic authorization, ballot encryption, and blockchain technology**.

The system is designed to provide:

- Voter eligibility verification
- One-person-one-vote enforcement
- Ballot confidentiality
- Voter privacy
- Reduced identity-to-ballot linkability
- Replay and double-voting protection
- Tamper detection
- Blockchain-based auditability

## System Architecture

The system is divided into three major components:

### Person 1 - Voter Verification

Responsible for:

- Iris-based voter verification
- Voter eligibility checking
- Already-voted status checking
- Maintaining voter identity information

Biometric and identity information remains within the voter verification component and is not stored on the blockchain.

### Person 2 - Cryptography and Voting Authorization

Responsible for:

- Anonymous voting authorization
- RSA blind-signature based authorization
- Election-specific nullifier generation
- Ballot encryption using AES-GCM
- RSA-OAEP encryption of the ballot encryption key
- Protected voting package generation
- Cryptographic verification
- Replay protection

### Person 3 - Blockchain

Responsible for:

- Receiving the protected voting package
- Blockchain transaction processing
- Nullifier checking
- Recording voting transactions
- Returning blockchain confirmation and transaction hash
- Maintaining an auditable voting record

## Cryptographic Components

The current cryptographic implementation includes:

- **RSA blind signatures** for anonymous authorization
- **Ed25519** for voter-controlled anonymous key pairs
- **HMAC-SHA256** for election-specific nullifiers
- **AES-256-GCM** for ballot encryption
- **RSA-OAEP with SHA-256** for encryption of the ballot encryption key
- Secure random number generation for cryptographic randomness

## Privacy Model

The system separates voter identity from the voting process.

```text
Person 1
Identity + Biometrics + Eligibility
          |
          v
Person 2
Anonymous Authorization + Encryption + Nullifier
          |
          v
Person 3
Verification + Blockchain Recording
