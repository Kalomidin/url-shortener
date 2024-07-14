from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import schemas
from repository.database import get_db
import error
import repository.url_shortener as url_shortener_repo
import repository.url_stats as url_stats_repo

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
    existing_url = url_shortener_repo.find_url_shorten_by_url_id(db, url_id)
    if existing_url is not None:
        expired = url_shortener_repo.update_url_expiry(db, existing_url)
        if not expired:
            return schemas.CreateUrlShortenerResponse(short_url=existing_url.id.hex)
    d = url_shortener_repo.create_url_shorten(db, url, url_id, req.expiry_days)
    return schemas.CreateUrlShortenerResponse(short_url=d.id.hex)


@router.get("/{short_url}", status_code=status.HTTP_301_MOVED_PERMANENTLY)
def get_url(short_url: str, db: Session = Depends(get_db)):
    queryStatus = url_stats_repo.UrlStatus.OK
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
            url_stats_repo.create_url_stats(db, id, queryStatus)
        except Exception as e:
            print("Error adding stats", e)


def _get_url(id: uuid.UUID, db: Session) -> RedirectResponse:
    d = url_shortener_repo.find_url_shorten_by_id(db, id)
    if d is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERRNOTFOUND
        )

    # check if it is expired
    expired = url_shortener_repo.update_url_expiry(db, d)
    if expired:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERREXPIRED
        )
    return RedirectResponse(url=d.url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get("/stats/{short_url}", response_model=schemas.UrlStats)
def get_url_stats(short_url: str, db: Session = Depends(get_db)):
    id = None
    try:
        id = uuid.UUID(short_url)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.HTTPERRINVALIDURL
        )
    stats = url_stats_repo.get_url_stats(db, id)
    resp = schemas.UrlStats(url_id=id.hex, status_counts={})
    for s in stats:
        resp.status_counts[s.status.name] = resp.status_counts.get(s.status.name, 0) + 1
    return resp


def url_to_uuid(url):
    return uuid.uuid5(uuid.NAMESPACE_URL, url)
