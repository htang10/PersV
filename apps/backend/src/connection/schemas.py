from enum import StrEnum
from pathlib import Path
from typing import Annotated, ClassVar, Generic, Literal, Self, TypeVar

from pydantic import ConfigDict, Field, TypeAdapter, model_validator
from sqlalchemy import URL

from src.core.schemas import CustomBaseModel


class DBMS(StrEnum):
    """Supported database management systems and their SQLAlchemy URL schemes."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    MSSQL = "mssql"

    @property
    def scheme(self) -> str:
        """Returns the SQLAlchemy connection scheme for the database driver."""
        return {
            DBMS.POSTGRESQL: "postgresql+psycopg",
            DBMS.MYSQL: "mysql+pymysql",
            DBMS.MARIADB: "mariadb+pymysql",
            DBMS.SQLITE: "sqlite+pysqlite",
            DBMS.ORACLE: "oracle+oracledb",
            DBMS.MSSQL: "mssql+mssqlpython",
        }[self]


SCHEMA_DBMS = {DBMS.POSTGRESQL, DBMS.MSSQL, DBMS.ORACLE}
ClientServerDBMS = Literal[
    DBMS.POSTGRESQL, DBMS.MYSQL, DBMS.MARIADB, DBMS.ORACLE, DBMS.MSSQL
]


class ClientServerConnectionConfig(CustomBaseModel):
    """Connection settings for a client-server database."""

    dbms: ClientServerDBMS = Field(
        description="The database management system hosting the target database.",
    )
    username: str = Field(
        description="The username used to authenticate with the database server.",
    )
    password: str = Field(
        description="The password used to authenticate with the database server.",
    )
    host: str = Field(
        description="The hostname or IP address of the database server.",
    )
    port: int = Field(
        ge=1,
        le=65535,
        description="The port number the database server is listening on.",
    )
    db: str = Field(
        description="The name of the database to connect to.",
    )
    db_schema: str | None = Field(
        default=None,
        alias="schema",
        description="The schema to use when connecting to the database.",
    )

    @model_validator(mode="after")
    def validate_schema(self) -> Self:  # from typing import Self
        """Require a schema for DBMSs that use schemas and discard it otherwise."""
        if self.dbms in SCHEMA_DBMS and not self.db_schema:
            raise ValueError("A schema is required for this database.")
        if self.dbms not in SCHEMA_DBMS:
            self.db_schema = None
        return self

    def to_url(self) -> URL:
        """Build a SQLAlchemy URL from the connection settings."""
        if self.dbms == DBMS.ORACLE:
            database, query = None, {"service_name": self.db}
        else:
            database, query = self.db, {}

        return URL.create(
            drivername=self.dbms.scheme,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=database,
            query=query,
        )


class EmbeddedConnectionConfig(CustomBaseModel):
    """Connection settings for an embedded SQLite database file."""

    dbms: ClassVar[DBMS] = DBMS.SQLITE

    db_path: str = Field(
        description="The filesystem path to the SQLite database file.",
    )

    def to_url(self) -> URL:
        """Build a read-only SQLAlchemy URL for the SQLite database file."""
        query = {"mode": "ro", "uri": "true"}
        path = Path(self.db_path).resolve().as_posix()
        return URL.create(
            drivername=self.dbms.scheme, database=f"file:{path}", query=query
        )


class SQLiteUpload(CustomBaseModel):
    """Metadata for an uploaded SQLite database file."""

    file_path: str
    file_name: str


class ConnectionStatus(CustomBaseModel):
    """Report whether a database connection is established and its database name."""

    connected: bool
    database: str | None = Field(
        default=None,
        description="Name of the connected database, or 'null' if not connected.",
    )


class ConnectionPayload(CustomBaseModel):
    """Shared connection metadata returned by the connection endpoints."""

    db_schema: str | None = None
    connected_at: str


class DemoPayload(ConnectionPayload):
    """Identify an active connection to the built-in demo database."""

    target: Literal["demo"] = "demo"


class CustomPayload(ConnectionPayload):
    """Identify an active custom connection and its connection details."""

    target: Literal["custom"] = "custom"
    connection_details: ConnectionDetails


class ConnectionDetails(CustomBaseModel):
    """Store the metadata needed to identify and restore a custom connection."""

    dbms: str
    encrypted_url: str
    db: str | None
    db_file_path: str | None = None  # set only for uploaded SQLite files


ConnectionRecord = Annotated[
    DemoPayload | CustomPayload,
    Field(discriminator="target"),
]
connection_adapter = TypeAdapter(ConnectionRecord)


class QueryRequest(CustomBaseModel):
    """Represent a user's natural-language database query request."""

    prompt: str = Field(max_length=2000, description="The prompt user entered.")


EngineT = TypeVar("EngineT")
AgentT = TypeVar("AgentT")


class CacheEntry(CustomBaseModel, Generic[EngineT, AgentT]):
    """Hold the database engine and agent associated with a connection."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    target: str
    engine: EngineT | None
    agent: AgentT | None


class DemoCacheEntry(CacheEntry):
    """Represent a demo connection without a dedicated engine or agent."""

    target: Literal["demo"] = "demo"
    engine: Literal[None] = None
    agent: Literal[None] = None


class CustomCacheEntry(CacheEntry, Generic[EngineT, AgentT]):
    """Cache the engine, agent, and optional SQLite file path for a custom connection."""

    target: Literal["custom"] = "custom"
    engine: EngineT
    agent: AgentT
    db_file_path: str | None = None  # set only for uploaded SQLite files
