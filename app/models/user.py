from datetime import datetime, timezone, timedelta
import uuid

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, relationship

from app.database import Base
from app.auth.hashing import Hashing


class User(Base):
    __tablename__ = "users"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login = Column(DateTime, nullable=True)

    calculations = relationship(
        "Calculation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @classmethod
    def register(cls, db: Session, data: dict):
        """
        Register a new user. Expects keys:
        username, email, first_name, last_name, password
        """
        hashed_password = Hashing.get_password_hash(data["password"])
        user = cls(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=hashed_password,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.commit()  # ADD THIS LINE
        db.refresh(user)  # ADD THIS LINE
        return user

    def verify_password(self, plain_password: str) -> bool:
        return Hashing.verify_password(plain_password, self.password)

    @classmethod
    def authenticate(cls, db: Session, identifier: str, password: str):
        """
        Authenticate by username OR email.
        Returns User object if authentication succeeds, None otherwise.
        """
        user = (
            db.query(cls)
            .filter((cls.email == identifier) | (cls.username == identifier))
            .first()
        )

        if user is None:
            return None

        if not user.verify_password(password):
            return None

        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        return user

    @classmethod
    def update_last_login(cls, db: Session, user_id: uuid.UUID):
        user = db.query(cls).filter(cls.id == user_id).first()
        if user:
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
        return user

    @classmethod
    def verify_token(cls, token: str):
        """
        Verify a JWT token and return user data dict if valid, None otherwise.
        """
        from app.auth.jwt import decode_token
        from app.schemas.token import TokenType
        
        try:
            payload = decode_token(token, TokenType.ACCESS)
            user_id = payload.get("sub")
            username = payload.get("username")
            
            if not user_id:
                return None
            
            # Return dict matching test expectations
            return {
                "id": uuid.UUID(user_id),
                "username": username,
            }
        except Exception as e:
            print(f"verify_token error: {e}")  # ADD THIS FOR DEBUGGING
            return None