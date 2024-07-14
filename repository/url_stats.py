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
    Enum as AlchemyEnum,
    func,
)
from enum import Enum
from sqlalchemy.dialects.postgresql import insert as pg_insert


class UrlStatus(Enum):
    OK = 0
    NOT_FOUND = 1
    EXPIRED = 2


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


def create_url_stats(db, url_id: uuid.UUID, status: UrlStatus):
    stmt = pg_insert(UrlStats).values(url_id=url_id, status=status)
    db.connection().execute(stmt)
    db.commit()


def get_url_stats(db, url_id: uuid.UUID) -> list[UrlStats]:
    return db.query(UrlStats).filter(UrlStats.url_id == url_id).all()
