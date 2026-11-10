from enum import StrEnum
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


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
            DBMS.MYSQL: "mysql+mysqldb",
            DBMS.MARIADB: "mariadb+mariadbconnector",
            DBMS.SQLITE: "sqlite+pysqlite",
            DBMS.ORACLE: "oracle+oracledb",
            DBMS.MSSQL: "mssql+pyodbc",
        }[self]


class ConnectionConfig(BaseModel):
    """Database connection parameters provided by the user."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    dbms: DBMS = Field(
        default=DBMS.POSTGRESQL,
        description="The database management system hosting the target database.",
    )

    username: str | None = Field(
        default=None,
        description="The username used to authenticate with the database server.",
    )
    password: str | None = Field(
        default=None,
        description="The password used to authenticate with the database server.",
    )
    host: str | None = Field(
        default=None,
        description="The hostname or IP address of the database server.",
    )
    port: int | None = Field(
        default=None,
        description="The port number the database server is listening on.",
    )
    db: str | None = Field(
        default=None,
        description="The name of the database to connect to.",
    )
    db_path: str | None = Field(
        default=None,
        description="The filesystem path to the SQLite database file.",
    )
    db_schema: str | None = Field(
        default=None,
        alias="schema",
        description="The schema to use when connecting to the database.",
    )

    @model_validator(mode="after")
    def validate_connection_fields(self) -> ConnectionConfig:
        if self.dbms == DBMS.SQLITE:
            if not self.db_path:
                raise ValueError("A database file path is required for SQLite.")
        else:
            required_fields = {
                "username": self.username,
                "host": self.host,
                "port": self.port,
                "db": self.db,
            }

            missing = [
                field
                for field, value in required_fields.items()
                if value is None or value == ""
            ]

            if missing:
                raise ValueError(
                    f"The following fields are required: {', '.join(missing)}."
                )

        return self


class ConnectionStatus(BaseModel):
    connected: bool
    database: str | None = Field(
        default=None,
        description="Name of the connected database, or 'null' if not connected.",
    )


class ConnectionPayload(BaseModel):
    db_schema: str
    connected_at: str


class DemoPayload(ConnectionPayload):
    target: Literal["demo"] = "demo"


class CustomPayload(ConnectionPayload):
    target: Literal["custom"] = "custom"
    connection_details: ConnectionDetails


class ConnectionDetails(BaseModel):
    dbms: str
    url: str
    db: str | None


ConnectionRecord = Annotated[
    DemoPayload | CustomPayload,
    Field(discriminator="target"),
]
connection_adapter = TypeAdapter(ConnectionRecord)


class QueryRequest(BaseModel):
    prompt: str


EngineT = TypeVar("EngineT")
AgentT = TypeVar("AgentT")


class CacheEntry(BaseModel, Generic[EngineT, AgentT]):
    target: str
    engine: EngineT | None
    agent: AgentT | None


class DemoCacheEntry(CacheEntry):
    target: Literal["demo"] = "demo"
    engine: Literal[None] = None
    agent: Literal[None] = None


class CustomCacheEntry(CacheEntry, Generic[EngineT, AgentT]):
    target: Literal["custom"] = "custom"
    engine: EngineT
    agent: AgentT
