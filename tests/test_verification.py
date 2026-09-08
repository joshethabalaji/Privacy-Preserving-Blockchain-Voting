from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from crypto.voting_protocol import create_voting_package
from crypto.verification import VotingVerifier


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

voter_private_key = ed25519.Ed25519PrivateKey.generate()
voter_public_key = voter_private_key.public_key()

voter_public_key_bytes = voter_public_key.public_bytes_raw()


# -------------------------------------------------
# Create voting package
# -------------------------------------------------

package = create_voting_package(
    election_id="E2026",
    anonymous_private_key=voter_private_key,
    anonymous_public_key=voter_public_key_bytes,
    authorization_private_key=authorization_private_key,
    authorization_public_key=authorization_public_key,
    election_encryption_public_key=election_public_key,
    candidate="Candidate A"
)


# -------------------------------------------------
# Create Person 3 verifier
# -------------------------------------------------

verifier = VotingVerifier(
    authorization_public_key=authorization_public_key,
    election_id="E2026"
)


# -------------------------------------------------
# Test 1: First vote should be accepted
# -------------------------------------------------

first_vote = verifier.verify_package(package)

print("First vote accepted:", first_vote)

assert first_vote is True


# -------------------------------------------------
# Test 2: Same vote should be rejected
# -------------------------------------------------

second_vote = verifier.verify_package(package)

print("Replay vote rejected:", not second_vote)

assert second_vote is False


# -------------------------------------------------
# Test 3: Wrong election should be rejected
# -------------------------------------------------

wrong_election_package = package.copy()
wrong_election_package["election_id"] = "E2027"

wrong_election_result = verifier.verify_package(
    wrong_election_package
)

print("Wrong election rejected:", not wrong_election_result)

assert wrong_election_result is False


# -------------------------------------------------
# Test 4: Invalid authorization should be rejected
# -------------------------------------------------

invalid_auth_package = package.copy()

# Change one byte of the authorization signature
signature = invalid_auth_package["authorization_signature"]

replacement = "0" if signature[0] != "0" else "1"

invalid_auth_package["authorization_signature"] = (
    replacement + signature[1:]
)

invalid_auth_result = verifier.verify_package(
    invalid_auth_package
)

print("Invalid authorization rejected:", not invalid_auth_result)

assert invalid_auth_result is False


print("\nAll verification security tests PASSED.")