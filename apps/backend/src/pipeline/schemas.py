from enum import StrEnum
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


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
            DBMS.POSTGRESQL: "postgresql+psycopg2",
            DBMS.MYSQL: "mysql+mysqldb",
            DBMS.MARIADB: "mariadb+mariadbconnector",
            DBMS.SQLITE: "sqlite+pysqlite",
            DBMS.ORACLE: "oracle+oracledb",
            DBMS.MSSQL: "mssql+pyodbc",
        }[self]


class ConnectionConfig(BaseModel):
    """Database connection parameters provided by the user."""

    model_config = ConfigDict(extra="forbid")
    dbms: DBMS = Field(
        default=DBMS.POSTGRESQL,
        description="The database management system hosting the target database. Defaults to PostgreSQL.",
    )
    username: str = Field(
        description="The username used to authenticate with the database server."
    )
    password: str = Field(
        description="The password used to authenticate with the database server."
    )
    host: str = Field(description="The hostname or IP address of the database server.")
    port: int = Field(
        description="The port number the database server is listening on."
    )
    db: str = Field(description="The name of the database to connect to.")
    db_schema: str | None = Field(
        default=None,
        alias="schema",
        description="The schema to set as the search path. Only applicable to database systems that support schemas,"
        "such as PostgreSQL. Leave empty for others.",
    )


class SuccessConnection(BaseModel):
    status: str = Field(default="connected")
    database: str = Field(
        description="Database name is set as 'demo' if not specified.",
    )


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
