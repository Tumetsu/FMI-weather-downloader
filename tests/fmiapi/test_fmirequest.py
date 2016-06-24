from fmiapi.fmirequest import FMIRequest, RequestException
from datetime import datetime
from tests.testUtils import *
from tests.fmiapi.commonmocks import *
from unittest import mock
from lxml import etree
import pytz
import pytest

timezone = pytz.timezone('Europe/Helsinki')


class TestFMIRequest:
    def setup(self):
        self.xml_error = load_xml('./tests/fmiapi/testdata/error_response.xml')
        self.html_error = load_txt('./tests/fmiapi/testdata/other_html_error.html')

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_do_request_to_fmi_with_provided_query_params_and_return_data(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(200, '<asd>Important data</asd>')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))
        result = fmi_request.get(query)

        assert_equal(1, mock_connection.getresponse.call_count)
        assert_equal('Important data', result.text)

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_xml_response(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(400, etree.tostring(self.xml_error), content_type='text/xml; charset=UTF8')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(1916, 5, 23, hour=21, minute=31, second=57, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 5, 27, hour=21, minute=31, second=57, microsecond=0, tzinfo=timezone))

        with pytest.raises(RequestException) as e:
            fmi_request.get(query)

        assert_equal(400, e.value.error_code)
        assert 'Too long time interval \'1916-May-23 21:31:57\' to \'2011-May-27 21:31:57\'' in e.value.message

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_html_response(self, mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(404, self.html_error, content_type='text/html')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))

        with pytest.raises(RequestException) as e:
            fmi_request.get(query)

        assert_equal(404, e.value.error_code)
        assert 'Some module: Some random error' in e.value.html
