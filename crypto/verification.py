from crypto.authorization import verify_authorization


class VotingVerifier:
    """
    Simulates the verification performed by Person 3
    before accepting a voting package.
    """

    def __init__(
        self,
        authorization_public_key,
        election_id
    ):
        self.authorization_public_key = authorization_public_key
        self.election_id = election_id

        # In the real system, this will eventually be replaced
        # by blockchain storage / smart-contract state.
        self.used_nullifiers = set()

    def verify_package(self, package):
        """
        Verify an incoming protected voting package.

        Returns True if the package can be accepted.
        Returns False if any security check fails.
        """

        # -------------------------------------------------
        # 1. Check required fields
        # -------------------------------------------------

        required_fields = [
            "election_id",
            "anonymous_public_key",
            "authorization_signature",
            "prepared_message",
            "encrypted_ballot",
            "encrypted_key",
            "nonce",
            "nullifier"
        ]

        for field in required_fields:
            if field not in package:
                return False

        # -------------------------------------------------
        # 2. Check election
        # -------------------------------------------------

        if package["election_id"] != self.election_id:
            return False

        # -------------------------------------------------
        # 3. Convert cryptographic values from hex
        # -------------------------------------------------

        try:
            anonymous_public_key = bytes.fromhex(
                package["anonymous_public_key"]
            )

            authorization_signature = bytes.fromhex(
                package["authorization_signature"]
            )

            prepared_message = bytes.fromhex(
                package["prepared_message"]
            )

        except (ValueError, TypeError):
            return False

        # -------------------------------------------------
        # 4. Verify authorization
        # -------------------------------------------------

        authorization_valid = verify_authorization(
            self.authorization_public_key,
            self.election_id,
            anonymous_public_key,
            prepared_message,
            authorization_signature
        )

        if not authorization_valid:
            return False

        # -------------------------------------------------
        # 5. Check nullifier
        # -------------------------------------------------

        nullifier = package["nullifier"]

        if nullifier in self.used_nullifiers:
            return False

        # -------------------------------------------------
        # 6. Mark nullifier as used
        # -------------------------------------------------

        self.used_nullifiers.add(nullifier)

        return True