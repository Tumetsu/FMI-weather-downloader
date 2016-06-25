import http.client
import urllib.request
import pytz
from lxml import etree
from lxml import html
from fmiapi.fmierrors import *
import re


class FMIRequest:
    """
    This class provides a GET http-request to fetch a chunk of data.
    """

    def __init__(self, api_key):
        self._url = "data.fmi.fi"
        self._headers = {"Content-type": "text/xml"}
        self._connection = None
        self._XMLNS_NAMESPACE = {"xmlns": "http://www.opengis.net/ows/1.1"}

        self._apikey = api_key
        self._connection = http.client.HTTPConnection(self._url)

    def get(self, params):
        # Convert Finnish time to UTC here:
        params["starttime"] = params["starttime"].astimezone(pytz.utc)
        params["endtime"] = params["endtime"].astimezone(pytz.utc)
        self._connection.request("GET", "/fmi-apikey/{apikey}/wfs?{query_params}"
                                 .format(apikey=self._apikey,
                                         query_params=urllib.parse.urlencode(params)),
                                 headers=self._headers)
        response = self._connection.getresponse()
        if response.status == 200:
            data = response.read()
            return etree.XML(data)
        else:
            self._get_error_reason(response)

    def _get_error_reason(self, response):
        """
        FMI responds to some errors with HTML-page and some with XML-response. Figure out which one is the
        case and raise different error for further processing
        """
        if response.getheader("Content-Type") == "text/html":
            html_data = response.read()
            if 'Invalid fmi-apikey' in html_data:
                raise InvalidApikeyException()
            elif 'Query limit' in html_data:
                self._raise_query_limit_exception(html_data)
            else:
                raise RequestException("Error in html", response.status, html=response.read())

        elif response.getheader("Content-Type") == "text/xml; charset=UTF8":
            xml = etree.XML(response.read())
            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self._XMLNS_NAMESPACE).text,
                                   response.status)

    @staticmethod
    def _raise_query_limit_exception(html_str):
        """
        Try to find extra information from query limit response. Mainly waiting time and waiting unit
        until next query can be done.
        :param html_str:
        :return:
        """
        html_data = html.document_fromstring(html_str)
        elements = html_data.xpath('.//p[contains(text(),"Query limit")]')

        if len(elements) == 1:
            info = elements[0].text
            p = re.compile('Please wait (\d+) (seconds)')
            m = p.search(info)
            if m is not None:
                wait_time = m.group(1)
                wait_unit = m.group(2)
                raise QueryLimitException(wait_time=wait_time, wait_unit=wait_unit)
        raise QueryLimitException()
