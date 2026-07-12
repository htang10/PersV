from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base


class WalmartSales(Base):
    __tablename__ = "demo_walmart_sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int]
    start_date: Mapped[date]
    weekly_sales: Mapped[float]
    holiday: Mapped[bool]
    temperature: Mapped[float]
    fuel_price: Mapped[float]
    cpi: Mapped[float]
    unemployment_rate: Mapped[float]
