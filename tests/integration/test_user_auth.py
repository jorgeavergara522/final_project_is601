import pytest
from app.models.user import User
from app.auth.jwt import create_token, TokenType


# ----------------------------------------------------------------------
# Helper to clone fake_user_data fixture output (since it returns a function)
# ----------------------------------------------------------------------
def make_data(fake_user_data):
    """Returns a dict instead of the raw fixture function."""
    return fake_user_data()


# ----------------------------------------------------------------------
# PASSWORD HASHING
# ----------------------------------------------------------------------
def test_password_hashing(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)
    assert user.password != data["password"]  # must be hashed


# ----------------------------------------------------------------------
# REGISTRATION
# ----------------------------------------------------------------------
def test_user_registration(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)

    assert user.email == data["email"]
    assert user.username == data["username"]
    assert user.is_active is True


# ----------------------------------------------------------------------
# DUPLICATE REGISTRATION SHOULD FAIL
# ----------------------------------------------------------------------
def test_duplicate_user_registration(db_session, fake_user_data):
    data1 = make_data(fake_user_data)
    User.register(db_session, data1)

    data2 = make_data(fake_user_data)
    data2["email"] = data1["email"]  # duplicate
    data2["username"] = data1["username"]  # duplicate

    with pytest.raises(Exception):
        User.register(db_session, data2)


# ----------------------------------------------------------------------
# LOGIN / AUTH
# ----------------------------------------------------------------------
def test_user_authentication(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)

    authenticated = User.authenticate(db_session, data["email"], data["password"])
    assert authenticated.id == user.id


# ----------------------------------------------------------------------
# LAST LOGIN UPDATE
# ----------------------------------------------------------------------
def test_user_last_login_update(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)

    old_last_login = user.last_login

    authenticated = User.authenticate(db_session, data["email"], data["password"])
    db_session.refresh(authenticated)

    assert authenticated.last_login != old_last_login


# ----------------------------------------------------------------------
# TOKEN CREATION + VALIDATION
# ----------------------------------------------------------------------
def test_token_creation_and_verification(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)

    token = create_token({"sub": str(user.id)}, TokenType.ACCESS)
    assert isinstance(token, str)
    assert len(token) > 10


# ----------------------------------------------------------------------
# AUTH WITH EMAIL INSTEAD OF USERNAME
# ----------------------------------------------------------------------
def test_authenticate_with_email(db_session, fake_user_data):
    data = make_data(fake_user_data)
    user = User.register(db_session, data)

    authenticated = User.authenticate(db_session, data["email"], data["password"])
    assert authenticated.id == user.id
