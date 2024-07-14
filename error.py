from repository.models import UrlStatus

HTTPERRNOTFOUND = "URL not found"
HTTPERREXPIRED = "URL expired"
HTTPERRINVALIDURL = "Invalid URL"

map_status = {
    HTTPERRNOTFOUND: UrlStatus.NOT_FOUND,
    HTTPERREXPIRED: UrlStatus.EXPIRED,
    "": UrlStatus.OK,
}
