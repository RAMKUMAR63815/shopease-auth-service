from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.database.connection import Base, DATABASE_URL
from app.models import User


# Get Alembic configuration
config = context.config


# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Load SQLAlchemy model metadata
# Importing User ensures that its table is registered in Base.metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """
    Generate migration SQL without opening a database connection.
    """

    database_url = DATABASE_URL.render_as_string(
        hide_password=False
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Connect to MySQL and run migrations.
    """

    # Create an engine using settings from .env
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()

    finally:
        connectable.dispose()


# Select migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
