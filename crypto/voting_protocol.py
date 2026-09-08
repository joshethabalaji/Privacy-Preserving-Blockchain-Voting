from crypto.authorization import (
    create_authorization_request,
    issue_authorization,
    finalize_authorization,
    verify_authorization
)

from crypto.nullifier import generate_nullifier

from crypto.encryption import encrypt_ballot


def create_voting_package(
    election_id,
    anonymous_private_key,
    anonymous_public_key,
    authorization_private_key,
    authorization_public_key,
    election_encryption_public_key,
    candidate
):
    """
    Create the complete protected voting package that
    Person 2 sends to Person 3.
    """

    # -------------------------------------------------
    # 1. Create anonymous authorization request
    # -------------------------------------------------

    authorization_request = create_authorization_request(
        election_id,
        anonymous_public_key,
        authorization_public_key
    )

    # -------------------------------------------------
    # 2. Person 1 blindly signs the request
    # -------------------------------------------------

    blind_signature = issue_authorization(
        authorization_private_key,
        authorization_request["blinded_message"]
    )

    # -------------------------------------------------
    # 3. Person 2 finalizes the authorization
    # -------------------------------------------------

    authorization_signature = finalize_authorization(
        authorization_public_key,
        authorization_request["prepared_message"],
        blind_signature,
        authorization_request["inverse"]
    )

    # -------------------------------------------------
    # 4. Verify authorization before voting
    # -------------------------------------------------

    authorization_valid = verify_authorization(
        authorization_public_key,
        election_id,
        anonymous_public_key,
        authorization_request["prepared_message"],
        authorization_signature
    )

    if not authorization_valid:
        raise ValueError("Invalid voting authorization")

    # -------------------------------------------------
    # 5. Generate election-specific nullifier
    # -------------------------------------------------

    # The anonymous private key is used as the voter's
    # secret. The real voter identity is NOT used here.
    anonymous_secret = anonymous_private_key.private_bytes_raw()

    nullifier = generate_nullifier(
        anonymous_secret,
        election_id
    )

    # -------------------------------------------------
    # 6. Encrypt the ballot
    # -------------------------------------------------

    ballot = {
        "candidate": candidate
    }

    encrypted_package = encrypt_ballot(
        ballot,
        election_encryption_public_key
    )

    # -------------------------------------------------
    # 7. Create final protected voting package
    # -------------------------------------------------

    return {
        "election_id": election_id,
        "anonymous_public_key": anonymous_public_key.hex(),
        "authorization_signature": authorization_signature.hex(),
        "prepared_message": authorization_request["prepared_message"].hex(),
        "encrypted_ballot": encrypted_package["encrypted_ballot"],
        "encrypted_key": encrypted_package["encrypted_key"],
        "nonce": encrypted_package["nonce"],
        "nullifier": nullifier
    }