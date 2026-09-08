import hashlib
import hmac


DOMAIN_SEPARATOR = b"VotingSystem-Nullifier-v1"


def generate_nullifier(voter_secret, election_id):
    """
    Generate an election-specific nullifier.

    The same voter secret and election ID always produce
    the same nullifier.

    Different elections produce different nullifiers.

    The voter's real identity is never included.
    """

    if not isinstance(voter_secret, bytes):
        raise TypeError("Voter secret must be bytes")

    if not voter_secret:
        raise ValueError("Voter secret cannot be empty")

    if not isinstance(election_id, str):
        raise TypeError("Election ID must be a string")

    if not election_id:
        raise ValueError("Election ID cannot be empty")

    message = (
        DOMAIN_SEPARATOR
        + election_id.encode("utf-8")
    )

    nullifier = hmac.new(
        voter_secret,
        message,
        hashlib.sha256
    ).hexdigest()

    return nullifier