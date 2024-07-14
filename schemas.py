from pydantic import BaseModel


class CreateUrlShortenerRequest(BaseModel):
    url: str
    expiry_days: int | None = None


class CreateUrlShortenerResponse(BaseModel):
    short_url: str


class GetUrlShortenerResponse(BaseModel):
    url: str


class UrlStats(BaseModel):
    url_id: str
    statusCounts: dict[str, int]
