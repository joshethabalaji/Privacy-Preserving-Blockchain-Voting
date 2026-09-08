from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidTag

from crypto.encryption import (
    encrypt_ballot,
    decrypt_ballot
)


# Generate election encryption key pair
election_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072
)

election_public_key = election_private_key.public_key()


# Example ballot
ballot = {
    "candidate": "Candidate A"
}


# Encrypt ballot
encrypted_package = encrypt_ballot(
    ballot,
    election_public_key
)

print("Ballot encrypted:", True)
print(
    "Encrypted ballot length:",
    len(encrypted_package["encrypted_ballot"])
)
print(
    "Encrypted key length:",
    len(encrypted_package["encrypted_key"])
)
print(
    "Nonce generated:",
    bool(encrypted_package["nonce"])
)


# Decrypt ballot
decrypted_ballot = decrypt_ballot(
    encrypted_package,
    election_private_key
)

print("Ballot decrypted:", True)
print("Decrypted ballot:", decrypted_ballot)


# Verify original ballot
assert decrypted_ballot == ballot

print("\nEncryption/decryption test PASSED.")


# Test tampering detection
tampered_package = encrypted_package.copy()

# Change one character in the ciphertext
ciphertext = tampered_package["encrypted_ballot"]

replacement = "0" if ciphertext[0] != "0" else "1"

tampered_package["encrypted_ballot"] = (
    replacement + ciphertext[1:]
)

try:
    decrypt_ballot(
        tampered_package,
        election_private_key
    )

    print("Tampering detection FAILED.")

except InvalidTag:
    print("Tampering detected successfully.")
    print("Tampering detection test PASSED.")