from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter
from sqlalchemy.dialects.postgresql import insert as pg_insert
from fastapi.responses import RedirectResponse
import repository.models as models
import schemas
from repository.database import get_db
import error

router = APIRouter(prefix="/url_shortener", tags=["UrlShortener"])


@router.post(
    "/shorten",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateUrlShortenerResponse,
)
def create_url_shorten(
    req: schemas.CreateUrlShortenerRequest, db: Session = Depends(get_db)
):
    url = req.url
    url_id = url_to_uuid(url)
    id = url_to_uuid(url + datetime.now().isoformat())
    stmt = (
        pg_insert(models.UrlShortener)
        .values(id=id, url=url, url_id=url_id)
        .on_conflict_do_nothing()
    )
    db.connection().execute(stmt)
    db.commit()
    d: models.UrlShortener = (
        db.query(models.UrlShortener)
        .filter(
            models.UrlShortener.url_id == url_id, models.UrlShortener.expired == False
        )
        .first()
    )
    resp = schemas.CreateUrlShortenerResponse(short_url=d.id.hex)
    return resp


@router.get("/{short_url}", status_code=status.HTTP_301_MOVED_PERMANENTLY)
def get_url(short_url: str, db: Session = Depends(get_db)):
    queryStatus = models.UrlStatus.OK
    id = None
    try:
        id = uuid.UUID(short_url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERRINVALIDURL
        )
    try:
        return _get_url(id, db)
    except HTTPException as e:
        queryStatus = error.map_status[e.detail]
        raise e
    finally:
        try:
            stmt = (
                pg_insert(models.UrlStats)
                .values(url_id=id, status=queryStatus)
                .on_conflict_do_nothing()
            )
            db.connection().execute(stmt)
            db.commit()
            print("Stats added")
        except Exception as e:
            print("Error adding stats", e)


def _get_url(id: uuid.UUID, db: Session) -> RedirectResponse:
    d: models.UrlShortener = (
        db.query(models.UrlShortener)
        .filter(models.UrlShortener.id == id, models.UrlShortener.expired == False)
        .first()
    )
    if d is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERRNOTFOUND
        )
    # check if it is expired
    expired = datetime.now().replace(tzinfo=None) - d.created_at.replace(tzinfo=None)
    if expired.days > 7:
        d.expired = True
        d.updated_at = datetime.now()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERREXPIRED
        )

    return RedirectResponse(url=d.url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get("/stats/{short_url}", response_model=list[schemas.UrlStats])
def get_url_stats(short_url: str, db: Session = Depends(get_db)):
    id = None
    try:
        id = uuid.UUID(short_url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERRINVALIDURL
        )
    try:
        stats: list[models.UrlStats] = (
            db.query(models.UrlStats).filter(models.UrlStats.url_id == id).all()
        )
        resp = schemas.UrlStats(url_id=id.hex, statusCounts={})
        for s in stats:
            resp.statusCounts[s.status.name] = (
                resp.statusCounts.get(s.status.name, 0) + 1
            )
        return [resp]
    except HTTPException as e:
        raise e


def url_to_uuid(url):
    return uuid.uuid5(uuid.NAMESPACE_URL, url)
