from datetime import date
import uuid
from repository.database import Base
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Uuid,
    text,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert


class UrlShortener(Base):
    __tablename__ = "url_shortener"

    id: uuid.UUID = Column(Uuid, primary_key=True, nullable=False)
    url: str = Column(String, nullable=False)
    url_id: uuid.UUID = Column(Uuid, nullable=False)
    created_at: date = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: date = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    expired: bool = Column(Boolean, nullable=False, default=False)

    # Define an index with a partial condition
    __table_args__ = (
        Index(
            "unique_url_id_expired",
            url_id,
            expired,
            unique=True,
            postgresql_where=(expired == False),
        ),
    )

    def __repr__(self) -> str:
        return (
            "UrlShortener(id={self.id!r}, url={self.url!r}," + "url_id={self.url_id!r})"
        )


def create_url_shorten(db, id: uuid.UUID, url: str, url_id: uuid.UUID) -> UrlShortener:
    stmt = (
        pg_insert(UrlShortener)
        .values(id=id, url=url, url_id=url_id)
        .on_conflict_do_nothing()
    )
    db.connection().execute(stmt)
    db.commit()
    return find_url_shorten_by_url_id(db, url_id)


def find_url_shorten_by_url_id(db, url_id: uuid.UUID) -> UrlShortener:
    return (
        db.query(UrlShortener)
        .filter(UrlShortener.url_id == url_id, UrlShortener.expired == False)
        .first()
    )


def find_url_shorten_by_id(db, id: uuid.UUID) -> UrlShortener:
    return (
        db.query(UrlShortener)
        .filter(UrlShortener.id == id, UrlShortener.expired == False)
        .first()
    )


def expire_url_shorten(db, d: UrlShortener):
    d.expired = True
    db.commit()
