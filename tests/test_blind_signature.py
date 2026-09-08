from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from crypto.blind_signature import (
    prepare,
    blind,
    blind_sign,
    finalize,
    verify
)


# Generate a dedicated RSA key pair for the
# blind-signature protocol.
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072
)

public_key = private_key.public_key()


# Voter's private message
message = b"anonymous-voter-credential"


# 1. Prepare
prepared_message = prepare(message)


# 2. Blind
blinded_message, inverse = blind(
    public_key,
    prepared_message
)


# 3. Person 1 blind-signs
blind_signature = blind_sign(
    private_key,
    blinded_message
)


# 4. Voter finalizes
signature = finalize(
    public_key,
    prepared_message,
    blind_signature,
    inverse
)


# 5. Verify
valid = verify(
    public_key,
    prepared_message,
    signature
)


print("Prepared message generated:", prepared_message is not None)
print("Blinded message generated:", blinded_message is not None)
print("Blind signature generated:", blind_signature is not None)
print("Final signature generated:", signature is not None)
print("Signature valid:", valid)

if valid:
    print("\nBlind signature test PASSED.")
else:
    print("\nBlind signature test FAILED.")