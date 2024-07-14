from datetime import datetime, timedelta, date
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
    Enum as AlchemyEnum,
    func,
)
from enum import Enum


class UrlStatus(Enum):
    OK = 0
    NOT_FOUND = 1
    EXPIRED = 2


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


class UrlStats(Base):
    __tablename__ = "url_stats"

    id: uuid.UUID = Column(Uuid, primary_key=True, nullable=False, default=uuid.uuid4)
    url_id: uuid.UUID = Column(Uuid, nullable=False)
    status: UrlStatus = Column(AlchemyEnum(UrlStatus), nullable=False, default=0)
    created_at: date = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: date = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    # Define an index on url_id column
    __table_args__ = (Index("index_url_id", "url_id"),)

    def __repr__(self) -> str:
        return "UrlStats(url_id={self.url_id!r}, status={self.status!r})"
