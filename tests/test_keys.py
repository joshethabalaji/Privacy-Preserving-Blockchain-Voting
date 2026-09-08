from keys import (
    generate_authorization_keypair,
    generate_election_encryption_keypair,
    generate_voter_signing_keypair
)


# Person 1's authorization keys
auth_private, auth_public = generate_authorization_keypair()

# Election encryption keys
enc_private, enc_public = generate_election_encryption_keypair()

# Voter's anonymous signing keys
voter_private, voter_public = generate_voter_signing_keypair()


print("Authorization key generated:", auth_private is not None)
print("Authorization public key generated:", auth_public is not None)

print("Election encryption key generated:", enc_private is not None)
print("Election public key generated:", enc_public is not None)

print("Voter private key generated:", voter_private is not None)
print("Voter public key generated:", voter_public is not None)

print("\nAll key generation tests completed successfully.")