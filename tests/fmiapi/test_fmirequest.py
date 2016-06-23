from fmiapi.fmirequest import FMIRequest, RequestException
from datetime import datetime
from tests.testUtils import *
from unittest import mock
from lxml import etree
import pytz
import pytest

timezone = pytz.timezone('Europe/Helsinki')


class MockResponse:
    def __init__(self, status, data, content_type='text/xml; charset=UTF8'):
        self.status = status
        self.data = data
        self.content_type = content_type

    def read(self):
        return self.data

    def getheader(self, header):
        if header == 'Content-Type':
            return self.content_type




class TestFMIRequest:
    def setup(self):
        lxmlParser = etree.XMLParser(encoding='utf-8')
        tree = etree.parse('./tests/fmiapi/testdata/error_response.xml', parser=lxmlParser)
        self.xml_error = tree.getroot()

        with open('./tests/fmiapi/testdata/invalid_apikey_error.html', 'r', encoding='utf-8') as f:
            self.html_error = f.read()
            f.close()

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_do_request_to_fmi_with_provided_query_params_and_return_data(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(200, '<asd>Important data</asd>')
        fmi_request = FMIRequest('apikey')

        result = fmi_request.get({'starttime': datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                    'endtime': datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                    'fmisid': '1234',
                    'request': 'getFeature',
                    'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage'
                    })

        assertEqual(1, mock_connection.getresponse.call_count)
        assertEqual('Important data', result.text)

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_xml_response(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(400, etree.tostring(self.xml_error), content_type='text/xml; charset=UTF8')
        fmi_request = FMIRequest('apikey')

        with pytest.raises(RequestException) as e:
            fmi_request.get(
                {'starttime': datetime(1916, 5, 23, hour=21, minute=31, second=57, microsecond=0, tzinfo=timezone),
                 'endtime': datetime(2011, 5, 27, hour=21, minute=31, second=57, microsecond=0, tzinfo=timezone),
                 'fmisid': '1234',
                 'request': 'getFeature',
                 'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage'
                 })

        assertEqual(400, e.value.error_code)
        assert 'Too long time interval \'1916-May-23 21:31:57\' to \'2011-May-27 21:31:57\'' in e.value.message

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_html_response(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(404, self.html_error,
                                                                content_type='text/html')
        fmi_request = FMIRequest('apikey')

        with pytest.raises(RequestException) as e:
            fmi_request.get(
                {'starttime': datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                 'endtime': datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                 'fmisid': '1234',
                 'request': 'getFeature',
                 'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage'
                 })

        assertEqual(404, e.value.error_code)
        assert 'fmi-apikey mapper: Invalid fmi-apikey' in e.value.html