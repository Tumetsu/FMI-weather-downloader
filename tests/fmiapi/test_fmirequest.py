from fmiapi.fmirequest import FMIRequest, RequestException
from fmiapi.fmixmlparser import FMIxmlParser
from datetime import datetime

from tests.fmiapi.testdata.expected_data import EXPECTED_REALTIME_1_DAY
from tests.testUtils import *
from tests.fmiapi.commonmocks import *
from unittest import mock
from lxml import etree
import pytz
import pytest
timezone = pytz.timezone('Europe/Helsinki')


def describe_fmi_request():
    xml_error = load_xml('./tests/fmiapi/testdata/error_response.xml')
    html_error = load_txt('./tests/fmiapi/testdata/other_html_error.html')

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_do_request_to_fmi_with_provided_query_params_and_return_data(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(200, '<asd>Important data</asd>')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(2010, 1, 1, hour=2, minute=1, second=0, microsecond=0),
                                   datetime(2011, 1, 5, hour=2, minute=1, second=0, microsecond=0))
        result = fmi_request.get(query)

        assert_equal(1, mock_connection.getresponse.call_count)
        assert_equal('Important data', result.text)

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_xml_response(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(400, etree.tostring(xml_error), content_type='text/xml; charset=UTF8')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(1916, 5, 23, hour=21, minute=31, second=57, microsecond=0),
                                   datetime(2011, 5, 27, hour=21, minute=31, second=57, microsecond=0))

        with pytest.raises(RequestException) as e:
            fmi_request.get(query)

        assert_equal(400, e.value.error_code)
        assert 'Too long time interval \'1916-May-23 21:31:57\' to \'2011-May-27 21:31:57\'' in e.value.message

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_get_exception_reason_from_html_response(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(404, html_error.encode('utf-8'), content_type='text/html')
        fmi_request = FMIRequest('apikey')
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0),
                                   datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0))

        with pytest.raises(RequestException) as e:
            fmi_request.get(query)

        assert_equal(404, e.value.error_code)
        assert 'Some module: Some random error' in e.value.html

    def describe_forbidden_range_error_recovery():
        """
        FMI-api has a quirk where it will return out of range error if request's timespan begins before allowed
        datetime. For example in Lammi Pappila station realtime data begins in 01.01.2010 02:00. If beginning time is
        before this limit, an exception response is given which includes lowerlimit date in human readable format.
        App tries to parse this lowerlimit datetime out from response and retry given request by replacing the beginning
        time with found lowerlimit value. These tests try to ensure that finding process failures are handled correctly.

        Interestingly enough FMI api returns just empty data response for possible upperlimit cases so there is no need
        for similar process for requests into future.
        :return:
        """
        realtime_1_day = load_xml('./tests/fmiapi/testdata/realtime_1_day.xml')
        out_of_allowed_range_error = load_xml('./tests/fmiapi/testdata/out_of_allowed_range_error.xml')
        out_of_allowed_no_lowerlimit = load_xml('./tests/fmiapi/testdata/out_of_allowed_no_lowerlimit.xml')
        out_of_allowed_invalid_lowerlimit = load_xml('./tests/fmiapi/testdata/out_of_allowed_invalid_lowerlimit.xml')

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_try_to_find_lower_limit_datetime_if_out_of_range_response_encountered_and_try_again_with_it(mock_httpconn):
            # case where server returns out of range exception and we find instead new lower limit to retrieve with.
            # in short, first get failure with out of range, then do a new request with success
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(400, etree.tostring(out_of_allowed_range_error)),
                                                       MockResponse(200, etree.tostring(realtime_1_day))]

            fmi_request = FMIRequest('apikey')
            query = create_daily_query(datetime(2012, 1, 9, hour=2, minute=1, second=0, microsecond=0),
                                       datetime(2012, 1, 14, hour=2, minute=1, second=0, microsecond=0))
            result = fmi_request.get(query)
            # Make sure that the request was retried
            assert_equal(2, mock_connection.getresponse.call_count)

            # Returned dataframe should have all data available in provided xml
            parser = FMIxmlParser()
            result = parser.parse(result)
            verify_dataframe(result, EXPECTED_REALTIME_1_DAY)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_raise_general_request_exception_if_lowerlimit_cannot_be_found(mock_httpconn):
            # case where error won't contain lowerlimit and regular exception should be thrown
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(400, etree.tostring(out_of_allowed_no_lowerlimit))]

            fmi_request = FMIRequest('apikey')
            query = create_daily_query(datetime(2012, 1, 9, hour=2, minute=1, second=0, microsecond=0),
                                       datetime(2012, 1, 14, hour=2, minute=1, second=0, microsecond=0))

            with pytest.raises(RequestException) as e:
                fmi_request.get(query)

            # Should raise RequestException with information given by FMIApi in xml
            assert_equal(400, e.value.error_code)
            assert 'This is just a random error' in e.value.message

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_raise_general_request_exception_if_lowerlimit_date_cannot_be_parsed(mock_httpconn):
            # case where error's datetime is in invalid or unsupported format
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(400, etree.tostring(out_of_allowed_invalid_lowerlimit))]

            fmi_request = FMIRequest('apikey')
            query = create_daily_query(datetime(2012, 1, 9, hour=2, minute=1, second=0, microsecond=0),
                                       datetime(2012, 1, 14, hour=2, minute=1, second=0, microsecond=0))

            with pytest.raises(RequestException) as e:
                fmi_request.get(query)

            # Should raise RequestException with information given by FMIApi in xml
            assert_equal(400, e.value.error_code)
            assert 'value 2012-Tam-13 00:00:00 is out of allowed range' in e.value.message

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_not_get_into_infinite_recursion_if_lower_limit_is_invalid_and_throw_regular_regquest_exception(mock_httpconn):
            # case where error's lowerlimit for some reason won't work and recursion should be stopped after one
            # retry and throw Request exception with error code 400.
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(400, etree.tostring(out_of_allowed_range_error)),
                                                       MockResponse(400, etree.tostring(out_of_allowed_range_error)),
                                                       MockResponse(400, etree.tostring(out_of_allowed_range_error))]

            fmi_request = FMIRequest('apikey')
            query = create_daily_query(datetime(2012, 1, 9, hour=2, minute=1, second=0, microsecond=0),
                                       datetime(2012, 1, 14, hour=2, minute=1, second=0, microsecond=0))

            with pytest.raises(RequestException) as e:
                fmi_request.get(query)

            # Make sure that the request was retried
            assert_equal(2, mock_connection.getresponse.call_count)

            # Should raise RequestException with information given by FMIApi in xml
            assert_equal(400, e.value.error_code)
            assert 'Couldn\'t retrieve data even with found lowerlimit date' in e.value.message
