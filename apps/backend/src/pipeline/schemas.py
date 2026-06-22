from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DBMS(StrEnum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    MSSQL = "mssql"

    @property
    def scheme(self) -> str:
        return {
            DBMS.POSTGRESQL: "postgresql+psycopg2",
            DBMS.MYSQL: "mysql+mysqldb",
            DBMS.MARIADB: "mariadb+mariadbconnector",
            DBMS.SQLITE: "sqlite+pysqlite",
            DBMS.ORACLE: "oracle+oracledb",
            DBMS.MSSQL: "mssql+pyodbc",
        }[self]


class ConnectionConfig(BaseModel):
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
