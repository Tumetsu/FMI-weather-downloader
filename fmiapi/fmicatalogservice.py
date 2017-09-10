import http.client
import urllib.request
from lxml import etree
from datetime import datetime
from fmiapi.fmierrors import RequestException, NoDataSetsException

_NAMESPACES = {"csw": "http://www.opengis.net/cat/csw/2.0.2",
               "gmd": "http://www.isotc211.org/2005/gmd",
               "gco": "http://www.isotc211.org/2005/gco",
               "gml": "http://www.opengis.net/gml",
               "ows": "http://www.opengis.net/ows"}
_RETRIEVAL_RETRY_COUNT = 3


def _response_was_exception(data):
    """
    FMI api sometimes responses with XML exceptions from their internal systems. Try
    to detect it
    :return:
    """

    exception_found = data.find(".//ows:Exception", namespaces=_NAMESPACES)
    return exception_found is not None


def _retrieve_metadata_by_fmisid(fmisid, request_retry=0):
    url = "catalog.fmi.fi"
    headers = {"Content-type": "text/xml"}
    connection = http.client.HTTPConnection(url)

    params = {
        "service": "CSW",
        "version": "2.0.2",
        "request": "GetRecords",
        "resultType": "results",
        "outputSchema": "http://www.isotc211.org/2005/gmd",
        "NAMESPACE": "xmlns(gmd=http://www.isotc211.org/2005/gmd)",
        "typeNames": "gmd:MD_Metadata",
        "elementSetName": "full",
        "startPosition": 1,
        "maxRecords": 100,
        "CONSTRAINTLANGUAGE": "CQL_TEXT",
        "CONSTRAINT": "AnyText ='" + fmisid + "'",
        "CONSTRAINT_LANGUAGE_VERSION": "1.1.0"
    }

    connection.request("GET", "/geonetwork/srv/csw?{query_params}"
                       .format(query_params=urllib.parse.urlencode(params)),
                       headers=headers)

    response = connection.getresponse()
    if response.status == 200:
        data = etree.XML(response.read())

        if _response_was_exception(data):
            # Looks like we got an exception. Most likely this is random error on FMI's side, so try
            # again couple of times before giving up
            if request_retry < _RETRIEVAL_RETRY_COUNT:
                return _retrieve_metadata_by_fmisid(fmisid, request_retry=request_retry+1)
            else:
                raise RequestException("Error in metadata retrieval for fmisid " + fmisid, 'METADATA_RETRIEVAL')

        return data
    else:
        raise RequestException("Error in metadata retrieval for fmisid " + fmisid, 'METADATA_RETRIEVAL')


def _parse_data(data):
    """
    Parse catalog xml and pick interesting metadata from each search result
    :param data:
    :return:
    """
    records = data.find(".//csw:SearchResults", namespaces=_NAMESPACES)
    result = []

    def convert_to_date(datestr):
        if datestr is not None:
            return datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')
        else:
            return datestr

    for item in records:
        ds = {
            "title_fi": item.find(".//gmd:title/gco:CharacterString", namespaces=_NAMESPACES).text,
            "starttime": convert_to_date(
                item.find(".//gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition",
                          namespaces=_NAMESPACES).text),
            "endtime": convert_to_date(item.find(".//gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition",
                                                 namespaces=_NAMESPACES).text),
            "longitude": float(item.find(".//gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal",
                                         namespaces=_NAMESPACES).text),
            "latitude": float(item.find(".//gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal",
                                        namespaces=_NAMESPACES).text),
            "link": item.find(".//gmd:distributionInfo//gmd:CI_OnlineResource/gmd:linkage/gmd:URL",
                              namespaces=_NAMESPACES).text,
            "identifier": item.find(".//gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString",
                                    namespaces=_NAMESPACES).text
        }
        result.append(ds)

    return sorted(list({v["title_fi"]: v for v in result}.values()), key=lambda x: x[
        'title_fi'])  # Remove duplicates with temporary dict where unique attribute is the key


def get_station_metadata(fmisid):
    result = _parse_data(_retrieve_metadata_by_fmisid(fmisid))
    if len(result) == 0:
        raise NoDataSetsException(fmisid)
    return result
