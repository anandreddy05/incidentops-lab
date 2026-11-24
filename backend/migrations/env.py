from logging.config import fileConfig

from alembic import context
from incidentops_lab_api.core.base import Base
from incidentops_lab_api.core.config import get_settings
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

# Alembic configuration
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all model modules here as they are created.
# This ensures their tables are registered in Base.metadata.

target_metadata = Base.metadata


def get_database_url() -> str:
    """Get the database URL from application settings."""
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""
    database_url = get_database_url()

    # Alembic's synchronous migration engine uses psycopg's
    # synchronous driver, while FastAPI uses psycopg's async driver.
    sync_url = make_url(database_url).set(drivername="postgresql+psycopg")

    connectable = engine_from_config(
        {"sqlalchemy.url": sync_url.render_as_string(hide_password=False)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
