from crypto.nullifier import generate_nullifier


# Simulated anonymous voter secrets
voter1_secret = b"voter1-secret-very-random-32bytes!"
voter2_secret = b"voter2-secret-very-random-32bytes!"


# Same voter, same election
nullifier1 = generate_nullifier(
    voter1_secret,
    "E2026"
)

nullifier2 = generate_nullifier(
    voter1_secret,
    "E2026"
)


# Same voter, different election
nullifier3 = generate_nullifier(
    voter1_secret,
    "E2027"
)


# Different voter, same election
nullifier4 = generate_nullifier(
    voter2_secret,
    "E2026"
)


print("Nullifier 1:", nullifier1)
print("Nullifier 2:", nullifier2)
print("Nullifier 3:", nullifier3)
print("Nullifier 4:", nullifier4)


# Test 1: Same voter + same election
assert nullifier1 == nullifier2

# Test 2: Same voter + different election
assert nullifier1 != nullifier3

# Test 3: Different voter + same election
assert nullifier1 != nullifier4


print("\nSame voter + same election: PASS")
print("Same voter + different election: PASS")
print("Different voter + same election: PASS")

print("\nNullifier test PASSED.")