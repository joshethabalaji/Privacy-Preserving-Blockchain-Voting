import json
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_ballot(ballot, election_public_key):
    """
    Encrypt a ballot using hybrid encryption.

    AES-256-GCM encrypts the ballot.
    RSA-OAEP encrypts the randomly generated AES key.
    """

    if not isinstance(ballot, dict):
        raise TypeError("Ballot must be a dictionary")

    # Convert ballot to deterministic JSON bytes
    ballot_data = json.dumps(
        ballot,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    # Generate a fresh 256-bit AES key
    aes_key = secrets.token_bytes(32)

    # Generate a fresh 96-bit GCM nonce
    nonce = secrets.token_bytes(12)

    # Encrypt ballot using AES-256-GCM
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(
        nonce,
        ballot_data,
        None
    )

    # Encrypt AES key using election RSA public key
    encrypted_key = election_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        "encrypted_ballot": ciphertext.hex(),
        "encrypted_key": encrypted_key.hex(),
        "nonce": nonce.hex()
    }


def decrypt_ballot(encrypted_package, election_private_key):
    """
    Decrypt a ballot using the election RSA private key.
    """

    if not isinstance(encrypted_package, dict):
        raise TypeError("Encrypted package must be a dictionary")

    try:
        ciphertext = bytes.fromhex(
            encrypted_package["encrypted_ballot"]
        )
        encrypted_key = bytes.fromhex(
            encrypted_package["encrypted_key"]
        )
        nonce = bytes.fromhex(
            encrypted_package["nonce"]
        )
    except (KeyError, ValueError) as error:
        raise ValueError("Invalid encrypted ballot package") from error

    # Recover AES key using RSA-OAEP
    aes_key = election_private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt and authenticate ballot using AES-GCM
    aesgcm = AESGCM(aes_key)

    ballot_data = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(ballot_data.decode("utf-8"))