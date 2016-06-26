import datetime
import http.client
import urllib.request
import pytz
from lxml import etree
from lxml import html
from fmiapi.fmierrors import *
import re
import pytz
timezone = pytz.timezone('Europe/Helsinki')

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

    def _do_timezone_conversions(self, params):
        # Convert Finnish time to UTC here:
        params["starttime"] = timezone.localize(params["starttime"])
        params["endtime"] = timezone.localize(params["endtime"])
        params["starttime"] = params["starttime"].astimezone(pytz.utc)
        params["endtime"] = params["endtime"].astimezone(pytz.utc)
        params["starttime"] = params["starttime"].strftime('%Y-%m-%dT%H:%M:%SZ')
        params["endtime"] = params["endtime"].strftime('%Y-%m-%dT%H:%M:%SZ')
        return params

    def get(self, params):
        params = self._do_timezone_conversions(params)
        return self._do_get(params)

    def _do_get(self, params, second_call=False):
        self._connection.request("GET", "/fmi-apikey/{apikey}/wfs?{query_params}"
                                 .format(apikey=self._apikey,
                                         query_params=urllib.parse.urlencode(params)),
                                 headers=self._headers)

        response = self._connection.getresponse()
        if response.status == 200:
            data = response.read()
            return etree.XML(data)
        else:
            result = self._get_error_reason(response)
            if result is not None and result['type'] == 'lowerlimit' and not second_call:
                # previous request failed because of lower limit. Do new request recursively with found
                # lower limit
                params['starttime'] = result['lowerlimit']
                params["starttime"] = params["starttime"].strftime('%Y-%m-%dT%H:%M:%SZ')
                return self._do_get(params, second_call=True)
            else:
                # otherwise raise general RequestException
                raise RequestException('Couldn\'t retrieve data even with found lowerlimit date {}'.format(result['lowerlimit']), response.status)

    def _get_error_reason(self, response):
        """
        FMI responds to some errors with HTML-page and some with XML-response. Figure out which one is the
        case and raise different error for further processing
        """
        if response.getheader("Content-Type") == "text/html":
            html_data = response.read().decode('utf-8')
            if 'Invalid fmi-apikey' in html_data:
                raise InvalidApikeyException()
            elif 'Query limit' in html_data:
                self._raise_query_limit_exception(html_data)
            else:
                raise RequestException("Error in html", response.status, html=response.read())

        elif response.getheader("Content-Type") == "text/xml; charset=UTF8":
            xml = etree.XML(response.read())
            if 'is out of allowed range' in etree.tostring(xml).decode('utf-8'):
                return self._handle_out_of_range_exception(response, xml)

            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self._XMLNS_NAMESPACE).text,
                                   response.status)

    def _handle_out_of_range_exception(self, response, xml):
        """
        FMI-api has a quirk where it will return out of range error if request's timespan begins before allowed
        datetime. For example in Lammi Pappila station realtime data begins in 01.01.2010 02:00. If beginning time is
        before this limit, an exception response is given which includes lowerlimit date in human readable format.
        App tries to parse this lowerlimit datetime out from response and retry given request by replacing the beginning
        time with found lowerlimit value.

        Interestingly enough FMI api returns just empty data response for possible upperlimit cases so there is no need
        for similar process for requests into future.

        :param response:
        :param xml:
        :return:
        """
        namespaces = {'xmlns': "http://www.opengis.net/ows/1.1"}
        elements = xml.findall('.//xmlns:ExceptionText', namespaces=namespaces)
        try:
            for el in elements:
                if 'out of allowed range' in el.text:
                    p = re.compile('lowerLimit=(.+)\)')
                    m = p.search(el.text)
                    if m is not None:
                        lower_limit = m.group(1)
                        lower_limit = datetime.datetime.strptime(lower_limit, '%Y-%b-%d %H:%M:%S')
                        return {
                            'type': 'lowerlimit',
                            'lowerlimit': lower_limit
                        }

            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self._XMLNS_NAMESPACE).text,
                                   response.status)
        except:
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
