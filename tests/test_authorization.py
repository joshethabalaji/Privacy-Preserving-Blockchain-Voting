from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from crypto.authorization import (
    create_authorization_request,
    issue_authorization,
    finalize_authorization,
    verify_authorization
)


# Generate authorization authority key pair
authorization_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072
)

authorization_public_key = authorization_private_key.public_key()


# Generate anonymous voter key pair
voter_private_key = ed25519.Ed25519PrivateKey.generate()
voter_public_key = voter_private_key.public_key()

anonymous_public_key = voter_public_key.public_bytes_raw()

election_id = "E2026"


# Create authorization request
request = create_authorization_request(
    election_id,
    anonymous_public_key,
    authorization_public_key
)

print("Authorization request created:", True)


# Person 1 blindly signs
blind_signature = issue_authorization(
    authorization_private_key,
    request["blinded_message"]
)

print("Blind authorization issued:", True)


# Person 2 finalizes
authorization_signature = finalize_authorization(
    authorization_public_key,
    request["prepared_message"],
    blind_signature,
    request["inverse"]
)

print("Authorization finalized:", True)


# Correct verification
valid = verify_authorization(
    authorization_public_key,
    election_id,
    anonymous_public_key,
    request["prepared_message"],
    authorization_signature
)

print("Authorization valid:", valid)

assert valid is True


# Test wrong election
wrong_election_valid = verify_authorization(
    authorization_public_key,
    "E2027",
    anonymous_public_key,
    request["prepared_message"],
    authorization_signature
)

print("Wrong election rejected:", not wrong_election_valid)

assert wrong_election_valid is False


# Generate another anonymous voter key
another_voter_private_key = ed25519.Ed25519PrivateKey.generate()
another_voter_public_key = another_voter_private_key.public_key()

another_anonymous_public_key = (
    another_voter_public_key.public_bytes_raw()
)


# Test wrong anonymous voter key
wrong_voter_valid = verify_authorization(
    authorization_public_key,
    election_id,
    another_anonymous_public_key,
    request["prepared_message"],
    authorization_signature
)

print("Wrong anonymous voter rejected:", not wrong_voter_valid)

assert wrong_voter_valid is False


print("\nAuthorization security test PASSED.")