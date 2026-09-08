import hashlib

from crypto.blind_signature import (
    prepare,
    blind,
    blind_sign,
    finalize,
    verify
)


def create_credential_message(election_id, anonymous_public_key):
    """Create the message that binds authorization to election + anonymous key."""

    if not isinstance(election_id, str):
        raise TypeError("Election ID must be a string")

    if not election_id:
        raise ValueError("Election ID cannot be empty")

    if not isinstance(anonymous_public_key, bytes):
        raise TypeError("Anonymous public key must be bytes")

    if not anonymous_public_key:
        raise ValueError("Anonymous public key cannot be empty")

    return hashlib.sha384(
        election_id.encode("utf-8") +
        anonymous_public_key
    ).digest()


def create_authorization_request(
    election_id,
    anonymous_public_key,
    authorization_public_key
):
    """
    Person 2 creates a blinded authorization request.
    """

    credential_message = create_credential_message(
        election_id,
        anonymous_public_key
    )

    prepared_message = prepare(credential_message)

    blinded_message, inverse = blind(
        authorization_public_key,
        prepared_message
    )

    return {
        "election_id": election_id,
        "anonymous_public_key": anonymous_public_key,
        "credential_message": credential_message,
        "prepared_message": prepared_message,
        "blinded_message": blinded_message,
        "inverse": inverse
    }


def issue_authorization(
    authorization_private_key,
    blinded_message
):
    """Person 1 blindly signs the authorization request."""

    return blind_sign(
        authorization_private_key,
        blinded_message
    )


def finalize_authorization(
    authorization_public_key,
    prepared_message,
    blind_signature,
    inverse
):
    """Person 2 removes the blinding factor."""

    return finalize(
        authorization_public_key,
        prepared_message,
        blind_signature,
        inverse
    )


def verify_authorization(
    authorization_public_key,
    election_id,
    anonymous_public_key,
    prepared_message,
    signature
):
    """
    Verify both:
    1. The authorization signature is valid.
    2. The authorization is bound to this election + anonymous key.
    """

    # Check the signature first
    if not verify(
        authorization_public_key,
        prepared_message,
        signature
    ):
        return False

    # The prepared message contains:
    #
    # [32-byte random prefix] + [credential message]
    #
    # Recover the credential message.
    prefix_length = 32

    if len(prepared_message) <= prefix_length:
        return False

    credential_message = prepared_message[prefix_length:]

    # Recreate the expected credential message
    expected_message = create_credential_message(
        election_id,
        anonymous_public_key
    )

    # Constant-time comparison
    return credential_message == expected_message