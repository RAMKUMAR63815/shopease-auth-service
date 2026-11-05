from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)

from app.database.connection import Base


class User(Base):
    # Name of the MySQL table
    __tablename__ = "users"

    # Prevent two users from registering with the same email
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    # Unique primary key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # User's full name
    full_name = Column(
        String(150),
        nullable=False,
    )

    # Email must be unique
    email = Column(
        String(255),
        nullable=False,
    )

    # Store the hashed password, never the original password
    password_hash = Column(
        String(255),
        nullable=False,
    )

    # Default role for a newly registered customer
    role = Column(
        String(30),
        nullable=False,
        default="CUSTOMER",
        server_default="CUSTOMER",
    )

    # New accounts are active by default
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    # Automatically record when the account is created
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    # Automatically update this timestamp when the ORM updates the row
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        # Do not include password_hash in the representation
        return (
            f"User(id={self.id}, "
            f"full_name={self.full_name!r}, "
            f"email={self.email!r}, "
            f"role={self.role!r}, " #represent the value. /displays the string with quotation marks.
            f"is_active={self.is_active})"
        )
