from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


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
        description="The target database management system. Defaults to PostgreSQL.",
    )
    username: str = Field(description="The database username.")
    password: str = Field(description="The database password.")
    host: str = Field(description="The host address of the database server.")
    port: int = Field(description="The port the database server is listening on.")
    db: str = Field(description="The name of the target database.")


class SuccessConnection(BaseModel):
    status: str = Field(default="connected")
    database: str = Field(
        default="demo", description="Database name is set as 'demo' if not specified."
    )


class ConnectionCheck(BaseModel):
    connected: bool
    database: str | None = Field(
        default=None,
        description="Name of the connected database, or 'null' if not connected.",
    )


class QueryResponse(BaseModel):
    """Response containing the query result and the generated SQL statement."""

    result: str = Field(description="The result of the query.")
    sql: str = Field(
        description="The SQL query that was generated and executed to get the result."
    )
