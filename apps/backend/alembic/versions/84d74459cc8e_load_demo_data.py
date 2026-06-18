"""Load demo data

Revision ID: 84d74459cc8e
Revises: d271a4152231
Create Date: 2026-06-12 08:12:54.057277

"""

from pathlib import Path
from typing import Sequence, Union, Any

from alembic import op
import sqlalchemy as sa
import polars as pl

# revision identifiers, used by Alembic.
revision: str = "84d74459cc8e"
down_revision: Union[str, Sequence[str], None] = "d271a4152231"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMN_MAP = {
    "Store": "store_id",
    "Date": "start_date",
    "Weekly_Sales": "weekly_sales",
    "Holiday_Flag": "holiday",
    "Temperature": "temperature",
    "Fuel_Price": "fuel_price",
    "CPI": "cpi",
    "Unemployment": "unemployment_rate",
}


def read_data(filepath: str) -> list[dict[str, Any]]:
    data = pl.read_csv(filepath, try_parse_dates=True)
    data = data.rename(COLUMN_MAP).with_columns(pl.col("holiday").cast(pl.Boolean))
    return data.rows(named=True)


def upgrade() -> None:
    """Upgrade schema."""
    demo_dataset = sa.table(
        "walmart_sales",
        sa.column("store_id"),
        sa.column("start_date"),
        sa.column("weekly_sales"),
        sa.column("holiday"),
        sa.column("temperature"),
        sa.column("fuel_price"),
        sa.column("cpi"),
        sa.column("unemployment_rate"),
    )

    filepath = Path(__file__).resolve().parents[2] / "data" / "walmart_sales.csv"
    demo_records = read_data(str(filepath))

    op.bulk_insert(demo_dataset, demo_records)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM walmart_sales")
