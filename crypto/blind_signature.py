import hashlib
import math
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# RFC 9474 recommended randomized variant:
# RSABSSA-SHA384-PSS-Randomized
HASH_LENGTH = 48          # SHA-384 output
SALT_LENGTH = 48          # RFC 9474
RANDOM_PREFIX_LENGTH = 32


def _mgf1(seed, mask_length):
    """MGF1 using SHA-384."""
    output = b""
    counter = 0

    while len(output) < mask_length:
        counter_bytes = counter.to_bytes(4, "big")
        output += hashlib.sha384(seed + counter_bytes).digest()
        counter += 1

    return output[:mask_length]


def _emsa_pss_encode(message, em_bits):
    """
    EMSA-PSS-ENCODE using SHA-384 and a 48-byte salt.
    """

    em_len = (em_bits + 7) // 8

    if em_len < HASH_LENGTH + SALT_LENGTH + 2:
        raise ValueError("RSA modulus is too small for SHA-384 PSS")

    # Hash the message
    message_hash = hashlib.sha384(message).digest()

    # RFC 9474 requires cryptographically secure randomness
    salt = secrets.token_bytes(SALT_LENGTH)

    # H = Hash(8 zero bytes || mHash || salt)
    h = hashlib.sha384(
        b"\x00" * 8 + message_hash + salt
    ).digest()

    # PS || 0x01 || salt
    ps_length = em_len - SALT_LENGTH - HASH_LENGTH - 2

    db = (
        b"\x00" * ps_length
        + b"\x01"
        + salt
    )

    # Mask DB using MGF1(H)
    db_mask = _mgf1(
        h,
        em_len - HASH_LENGTH - 1
    )

    masked_db = bytes(
        a ^ b
        for a, b in zip(db, db_mask)
    )

    # Clear unused leftmost bits
    unused_bits = 8 * em_len - em_bits

    if unused_bits:
        masked_db = bytes(
            [masked_db[0] & (0xFF >> unused_bits)]
        ) + masked_db[1:]

    return masked_db + h + b"\xbc"


def prepare(message):
    """
    RFC 9474 PrepareRandomize.

    Adds 32 bytes of fresh randomness to the message.
    """

    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")

    random_prefix = secrets.token_bytes(
        RANDOM_PREFIX_LENGTH
    )

    return random_prefix + message


def blind(public_key, prepared_message):
    """
    RFC 9474 Blind.

    Returns:
        blinded_message
        inverse
    """

    numbers = public_key.public_numbers()

    n = numbers.n
    e = numbers.e

    modulus_length = (n.bit_length() + 7) // 8
    em_bits = n.bit_length() - 1

    encoded_message = _emsa_pss_encode(
        prepared_message,
        em_bits
    )

    m = int.from_bytes(
        encoded_message,
        "big"
    )

    if m >= n:
        raise ValueError("Encoded message representative is too large")

    # Choose random r where gcd(r,n) = 1
    while True:
        r = secrets.randbelow(n - 1) + 1

        if math.gcd(r, n) == 1:
            break

    # r^e mod n
    r_to_e = pow(r, e, n)

    # Blind the encoded message
    blinded = (m * r_to_e) % n

    # Inverse of r modulo n
    inverse = pow(r, -1, n)

    blinded_message = blinded.to_bytes(
        modulus_length,
        "big"
    )

    return blinded_message, inverse


def blind_sign(private_key, blinded_message):
    """
    RFC 9474 BlindSign.

    Person 1 performs the RSA private-key operation
    on the blinded message.
    """

    private_numbers = private_key.private_numbers()

    n = private_numbers.public_numbers.n
    d = private_numbers.d
    e = private_numbers.public_numbers.e

    modulus_length = (n.bit_length() + 7) // 8

    if len(blinded_message) != modulus_length:
        raise ValueError("Invalid blinded message length")

    m = int.from_bytes(
        blinded_message,
        "big"
    )

    if m >= n:
        raise ValueError("Message representative out of range")

    # RSA private operation
    s = pow(m, d, n)

    # RFC 9474 signing consistency check
    if pow(s, e, n) != m:
        raise ValueError("RSA blind signing failed")

    return s.to_bytes(
        modulus_length,
        "big"
    )


def finalize(public_key, prepared_message, blind_signature, inverse):
    """
    RFC 9474 Finalize.

    Removes the blinding factor and verifies
    the resulting RSA-PSS signature.
    """

    numbers = public_key.public_numbers()

    n = numbers.n

    modulus_length = (n.bit_length() + 7) // 8

    if len(blind_signature) != modulus_length:
        raise ValueError("Invalid blind signature length")

    blind_sig_int = int.from_bytes(
        blind_signature,
        "big"
    )

    # Remove the blinding factor
    signature_int = (
        blind_sig_int * inverse
    ) % n

    signature = signature_int.to_bytes(
        modulus_length,
        "big"
    )

    # Verify the finalized signature
    public_key.verify(
        signature,
        prepared_message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA384()),
            salt_length=SALT_LENGTH
        ),
        hashes.SHA384()
    )

    return signature


def verify(public_key, prepared_message, signature):
    """
    Verify an RSA blind signature after finalization.

    Returns True if valid, otherwise False.
    """

    try:
        public_key.verify(
            signature,
            prepared_message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA384()),
                salt_length=SALT_LENGTH
            ),
            hashes.SHA384()
        )

        return True

    except Exception:
        return False