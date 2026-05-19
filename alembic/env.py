from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.db.base import Base

import app.models.course  # noqa: F401
import app.models.student  # noqa: F401
import app.models.user  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return str(settings.DATABASE_URL)


def include_object(
    obj: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Ignore DB objects not declared in this app's SQLAlchemy models.

    Prevents autogenerate from emitting DROP for unrelated tables in a shared database.
    """
    if type_ == "table":
        if reflected and name not in target_metadata.tables:
            return False
    elif type_ == "index" and reflected:
        table = getattr(obj, "table", None)
        table_name = getattr(table, "name", None)
        if table_name is not None and table_name not in target_metadata.tables:
            return False
    elif type_ in ("unique_constraint", "foreign_key_constraint", "check_constraint"):
        table = getattr(obj, "table", None)
        table_name = getattr(table, "name", None)
        if table_name is not None and table_name not in target_metadata.tables:
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        connect_args=settings.database_connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
