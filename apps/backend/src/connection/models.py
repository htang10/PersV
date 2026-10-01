from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DemoBase(DeclarativeBase):
    metadata = MetaData(schema="demo")


class Album(DemoBase):
    __tablename__ = "album"
    __table_args__ = (
        PrimaryKeyConstraint("album_id", name="album_pkey"),
        Index("album_artist_id_idx", "artist_id"),
    )

    album_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey(
            "artist.artist_id",
            name="album_artist_id_fkey",
        ),
        nullable=False,
    )


class Artist(DemoBase):
    __tablename__ = "artist"
    __table_args__ = (PrimaryKeyConstraint("artist_id", name="artist_pkey"),)

    artist_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Customer(DemoBase):
    __tablename__ = "customer"
    __table_args__ = (
        PrimaryKeyConstraint("customer_id", name="customer_pkey"),
        Index("customer_support_rep_id_idx", "support_rep_id"),
    )

    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    company: Mapped[str | None] = mapped_column(String(80), nullable=True)
    address: Mapped[str | None] = mapped_column(String(70), nullable=True)
    city: Mapped[str | None] = mapped_column(String(40), nullable=True)
    state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(40), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(24), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(24), nullable=True)
    email: Mapped[str] = mapped_column(String(60), nullable=False)
    support_rep_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "employee.employee_id",
            name="customer_support_rep_id_fkey",
        ),
        nullable=True,
    )


class Employee(DemoBase):
    __tablename__ = "employee"
    __table_args__ = (
        PrimaryKeyConstraint("employee_id", name="employee_pkey"),
        Index("employee_reports_to_idx", "reports_to"),
    )

    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reports_to: Mapped[int | None] = mapped_column(
        ForeignKey(
            "employee.employee_id",
            name="employee_reports_to_fkey",
        ),
        nullable=True,
    )
    birth_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    hire_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    address: Mapped[str | None] = mapped_column(String(70), nullable=True)
    city: Mapped[str | None] = mapped_column(String(40), nullable=True)
    state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(40), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(24), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(24), nullable=True)
    email: Mapped[str | None] = mapped_column(String(60), nullable=True)


class Genre(DemoBase):
    __tablename__ = "genre"
    __table_args__ = (PrimaryKeyConstraint("genre_id", name="genre_pkey"),)

    genre_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Invoice(DemoBase):
    __tablename__ = "invoice"
    __table_args__ = (
        PrimaryKeyConstraint("invoice_id", name="invoice_pkey"),
        Index("invoice_customer_id_idx", "customer_id"),
    )

    invoice_id: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "customer.customer_id",
            name="invoice_customer_id_fkey",
        ),
        nullable=False,
    )
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    billing_address: Mapped[str | None] = mapped_column(String(70), nullable=True)
    billing_city: Mapped[str | None] = mapped_column(String(40), nullable=True)
    billing_state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    billing_country: Mapped[str | None] = mapped_column(String(40), nullable=True)
    billing_postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class InvoiceLine(DemoBase):
    __tablename__ = "invoice_line"
    __table_args__ = (
        PrimaryKeyConstraint("invoice_line_id", name="invoice_line_pkey"),
        Index("invoice_line_invoice_id_idx", "invoice_id"),
        Index("invoice_line_track_id_idx", "track_id"),
    )

    invoice_line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    invoice_id: Mapped[int] = mapped_column(
        ForeignKey(
            "invoice.invoice_id",
            name="invoice_line_invoice_id_fkey",
        ),
        nullable=False,
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey(
            "track.track_id",
            name="invoice_line_track_id_fkey",
        ),
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class MediaType(DemoBase):
    __tablename__ = "media_type"
    __table_args__ = (PrimaryKeyConstraint("media_type_id", name="media_type_pkey"),)

    media_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Playlist(DemoBase):
    __tablename__ = "playlist"
    __table_args__ = (PrimaryKeyConstraint("playlist_id", name="playlist_pkey"),)

    playlist_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)


class PlaylistTrack(DemoBase):
    __tablename__ = "playlist_track"
    __table_args__ = (
        PrimaryKeyConstraint("playlist_id", "track_id", name="playlist_track_pkey"),
        Index("playlist_track_playlist_id_idx", "playlist_id"),
        Index("playlist_track_track_id_idx", "track_id"),
    )

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey(
            "playlist.playlist_id",
            name="playlist_track_playlist_id_fkey",
        ),
        nullable=False,
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey("track.track_id", name="playlist_track_track_id_fkey"),
        nullable=False,
    )


class Track(DemoBase):
    __tablename__ = "track"
    __table_args__ = (
        PrimaryKeyConstraint("track_id", name="track_pkey"),
        Index("track_album_id_idx", "album_id"),
        Index("track_genre_id_idx", "genre_id"),
        Index("track_media_type_id_idx", "media_type_id"),
    )

    track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("album.album_id", name="track_album_id_fkey"), nullable=True
    )
    media_type_id: Mapped[int] = mapped_column(
        ForeignKey("media_type.media_type_id", name="track_media_type_id_fkey"),
        nullable=False,
    )
    genre_id: Mapped[int | None] = mapped_column(
        ForeignKey("genre.genre_id", name="track_genre_id_fkey"), nullable=True
    )
    composer: Mapped[str | None] = mapped_column(String(220), nullable=True)
    milliseconds: Mapped[int] = mapped_column(Integer, nullable=False)
    bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
