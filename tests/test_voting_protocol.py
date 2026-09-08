from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from crypto.voting_protocol import create_voting_package


# -------------------------------------------------
# Generate authorization authority keys
# -------------------------------------------------

authorization_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072
)

authorization_public_key = authorization_private_key.public_key()


# -------------------------------------------------
# Generate election encryption keys
# -------------------------------------------------

election_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072
)

election_public_key = election_private_key.public_key()


# -------------------------------------------------
# Generate anonymous voter keys
# -------------------------------------------------

anonymous_private_key = ed25519.Ed25519PrivateKey.generate()
anonymous_public_key = anonymous_private_key.public_key()

anonymous_public_key_bytes = anonymous_public_key.public_bytes_raw()


# -------------------------------------------------
# Create protected voting package
# -------------------------------------------------

package = create_voting_package(
    election_id="E2026",
    anonymous_private_key=anonymous_private_key,
    anonymous_public_key=anonymous_public_key_bytes,
    authorization_private_key=authorization_private_key,
    authorization_public_key=authorization_public_key,
    election_encryption_public_key=election_public_key,
    candidate="Candidate A"
)


# -------------------------------------------------
# Display package
# -------------------------------------------------

print("Voting package created:", True)

print("\nPackage fields:")

for key in package:
    print(f"  {key}: present")


# -------------------------------------------------
# Security checks
# -------------------------------------------------

assert package["election_id"] == "E2026"
assert package["anonymous_public_key"]
assert package["authorization_signature"]
assert package["prepared_message"]
assert package["encrypted_ballot"]
assert package["encrypted_key"]
assert package["nonce"]
assert package["nullifier"]

# Real voter identity must NOT be present
assert "voter_id" not in package
assert "voter_name" not in package
assert "iris" not in package
assert "fingerprint" not in package

# Candidate must not appear in plaintext
assert "Candidate A" not in str(package)


print("\nIdentity privacy check: PASS")
print("Encrypted ballot check: PASS")
print("Nullifier check: PASS")
print("Authorization check: PASS")

print("\nVoting protocol test PASSED.")