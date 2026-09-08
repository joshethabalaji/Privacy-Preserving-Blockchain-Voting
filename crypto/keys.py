from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization


def generate_authorization_keypair():
    """
    Generate the RSA key pair used by Person 1
    for anonymous authorization.
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072
    )

    return private_key, private_key.public_key()


def generate_election_encryption_keypair():
    """
    Generate the RSA key pair used for protecting
    the AES ballot-encryption key.
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072
    )

    return private_key, private_key.public_key()


def generate_voter_signing_keypair():
    """
    Generate an ephemeral Ed25519 key pair for the voter.

    The private key remains with the voter.
    The public key acts as the anonymous voting identity
    for the current authorization.
    """

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    return private_key, public_key


def save_private_key(private_key, filename):
    """
    Save a private key in PEM format.
    """

    pem_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(filename, "wb") as file:
        file.write(pem_data)


def save_public_key(public_key, filename):
    """
    Save a public key in PEM format.
    """

    pem_data = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(filename, "wb") as file:
        file.write(pem_data)


def load_private_key(filename):
    """
    Load a private key from a PEM file.
    """

    with open(filename, "rb") as file:
        return serialization.load_pem_private_key(
            file.read(),
            password=None
        )


def load_public_key(filename):
    """
    Load a public key from a PEM file.
    """

    with open(filename, "rb") as file:
        return serialization.load_pem_public_key(
            file.read()
        )