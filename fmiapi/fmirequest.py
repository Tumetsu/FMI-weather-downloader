import http.client
import urllib.request
from lxml import etree
from fmiapi.fmierrors import *


class FMIRequest:
    """ This class does the actual single http-request required """

    def __init__(self, api_key):
        self._url = "data.fmi.fi"
        self._headers = {"Content-type": "text/xml"}
        self._connection = None
        self._XMLNS_NAMESPACE = {"xmlns": "http://www.opengis.net/ows/1.1"}

        self._apikey = api_key
        self._connection = http.client.HTTPConnection(self._url)

    def get(self, params):
        self._connection.request("GET", "/fmi-apikey/" + self._apikey + "/wfs?" + urllib.parse.urlencode(params),
                                 headers=self._headers)
        response = self._connection.getresponse()
        if response.status == 200:
            data = response.read()
            return etree.XML(data)
        else:
            self._get_error_reason(response)
            raise RequestException(self._get_error_reason(response), response.status)

    def _get_error_reason(self, response):
        if response.getheader("Content-Type") == "text/html":
            raise RequestException("Error in html", response.status, html=response.read())

        elif response.getheader("Content-Type") == "text/xml; charset=UTF8":
            xml = etree.XML(response.read())
            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self._XMLNS_NAMESPACE).text,
                                   response.status)
