from lxml import etree
import http.client
import urllib.request
from fmierrors import *

class FMIRequest():

    _url = "data.fmi.fi"
    _headers =  {"Content-type": "text/xml"}
    _connection = None
    XMLNS_NAMESPACE = {"xmlns" : "http://www.opengis.net/ows/1.1"}

    def __init__(self, api_key):
        self._apikey = api_key
        self._connection = http.client.HTTPConnection(self._url)

    def get(self, params):
        self._connection.request("GET", "/fmi-apikey/" + self._apikey + "/wfs?" + urllib.parse.urlencode(params),
                                headers=self._headers)
        response = self._connection.getresponse()
        print(response.status)
        if response.status == 200:
            data = response.read()
            return etree.XML(data)
        else:
            print(response.getheader("Content-Type"))
            self._getErrorReason(response)
            raise RequestException(self._getErrorReason(response), response.status)

    def _getErrorReason(self, response):
        if response.getheader("Content-Type") == "text/html":
            raise RequestException("Error in html", response.status, html=response.read())

        elif response.getheader("Content-Type") == "text/xml; charset=UTF8":
            xml = etree.XML(response.read())
            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self.XMLNS_NAMESPACE).text, response.status)

