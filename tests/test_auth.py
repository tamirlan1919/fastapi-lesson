from src.auth import hash_password, verify_password


def test_hash_password_changes_plain_text():
    password = 'strongpassword123'
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is True


def test_same_password():
    password = 'strongpassword123'
    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two
    assert verify_password(password, hash_one) is True
    assert verify_password(password, hash_two) is True

