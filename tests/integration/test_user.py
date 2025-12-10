# ======================================================================================
# tests/integration/test_user.py
# ======================================================================================
# Purpose: Demonstrate user model interactions with the database using pytest fixtures.
#          Relies on 'conftest.py' for database session management and test isolation.
# ======================================================================================

import uuid 
import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.models.user import User

logger = logging.getLogger(__name__)

# ======================================================================================
# Basic Connection & Session Tests
# ======================================================================================

def test_database_connection(db_session):
    """Verify DB connection using SELECT 1."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    logger.info("Database connection test passed.")


def test_managed_session(managed_db_session):
    """
    Test the managed_db_session for executing a simple query and
    verifying rollback behavior on invalid SQL.
    """
    session = managed_db_session

    # Valid query
    session.execute(text("SELECT 1"))

    # Invalid SQL to force rollback behavior
    try:
        session.execute(text("INVALID SQL"))
    except Exception as e:
        assert "syntax" in str(e).lower() or "no such" in str(e).lower()


# ======================================================================================
# Session Handling Tests
# ======================================================================================

def test_session_handling(db_session):
    """Demonstrate partial commits and rollback behavior."""
    initial_count = db_session.query(User).count()

    # Create user1 (valid)
    user1 = User(
        first_name="User",
        last_name="One",
        email="user1@example.com",
        username="user1",
        password="hashed_password",
    )
    db_session.add(user1)
    db_session.commit()

    # Create user2 (duplicate email → should fail)
    user2 = User(
        first_name="User",
        last_name="Two",
        email="user1@example.com",  # duplicate email
        username="user2",
        password="hashed_password",
    )
    db_session.add(user2)

    try:
        db_session.commit()
    except Exception:
        db_session.rollback()

    # Create user3 (valid)
    user3 = User(
        first_name="User",
        last_name="Three",
        email="user3@example.com",
        username="user3",
        password="hashed_password",
    )
    db_session.add(user3)
    db_session.commit()

    # Verify exactly 2 new users were committed
    assert db_session.query(User).count() == initial_count + 2


# ======================================================================================
# User Creation Tests
# ======================================================================================

def test_create_user_with_faker(db_session, faker):
    """Create a user using Faker and confirm it was saved."""
    user_data = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.unique.email(),
        "username": faker.unique.user_name(),
        "password": "hashed_password",
    }

    user = User(**user_data)

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == user_data["email"]

def test_create_multiple_users(db_session):
    """Create multiple users using unique IDs and verify insertion."""
    users = []
    for i in range(3):
        unique_id = uuid.uuid4().hex[:8]
        data = {
            "first_name": f"Test{i}",
            "last_name": f"User{i}",
            "email": f"test{unique_id}@example.com",
            "username": f"user{unique_id}",
            "password": "hashed_password",
        }
        user = User(**data)
        users.append(user)
        db_session.add(user)
    
    db_session.commit()
    
    for user in users:
        db_session.refresh(user)
        assert user.id is not None


# ======================================================================================
# Query Tests
# ======================================================================================

@pytest.fixture
def seed_users(db_session):
    """Seed 3 users for query tests."""
    created = []
    for i in range(3):
        unique_id = uuid.uuid4().hex[:8]
        u = User(
            first_name=f"Test{i}",
            last_name=f"User{i}",
            email=f"test{unique_id}@example.com",
            username=f"user{unique_id}",
            password="hashed_password",
        )
        db_session.add(u)
        created.append(u)
    
    db_session.commit()
    return created

# ======================================================================================
# Transaction Tests
# ======================================================================================

def test_transaction_rollback(db_session, faker):
    """Verify that rollback works properly after an error."""
    initial_count = db_session.query(User).count()

    # Add a user but force failure before commit
    user_data = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.unique.email(),
        "username": faker.unique.user_name(),
        "password": "hashed_password",
    }
    user = User(**user_data)
    db_session.add(user)

    try:
        db_session.execute(text("SELECT * FROM nonexistent_table"))
        db_session.commit()
    except Exception:
        db_session.rollback()

    assert db_session.query(User).count() == initial_count


# ======================================================================================
# Update Tests
# ======================================================================================

@pytest.fixture
def local_test_user(db_session):
    """Create a test user for update and other operations."""
    unique_id = uuid.uuid4().hex[:8]
    u = User(
        first_name="Test",
        last_name="User",
        email=f"test{unique_id}@example.com",
        username=f"user{unique_id}",
        password="hashed_password",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def test_update_with_refresh(db_session, local_test_user):
    """Update a user and verify the refresh reflects new values."""
    original_email = local_test_user.email

    new_email = "updated@example.com"
    local_test_user.email = new_email
    db_session.commit()
    db_session.refresh(local_test_user)

    assert local_test_user.email != original_email
    assert local_test_user.email == new_email
