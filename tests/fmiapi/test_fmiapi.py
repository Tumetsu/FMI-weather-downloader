# noinspection PyUnusedLocal
from fmiapi.fmiapi import FMIApi
from datetime import datetime
from fmiapi.fmierrors import InvalidApikeyException, QueryLimitException, NoDataException
from tests.testUtils import *
from tests.fmiapi.commonmocks import *
from unittest import mock
from lxml import etree
import pytz
import pytest
import copy
from tests.fmiapi.testdata.expected_data import *

timezone = pytz.timezone('Europe/Helsinki')


def describe_fmi_api():
    daily_4_days = load_xml('./tests/fmiapi/testdata/daily_4_days.xml')
    daily_12_days = load_xml('./tests/fmiapi/testdata/daily_12_days.xml')
    html_apikey_error = load_txt('./tests/fmiapi/testdata/invalid_apikey_error.html')
    html_querylimit_error = load_txt('./tests/fmiapi/testdata/querylimit_error.html')
    realtime_1_day = load_xml('./tests/fmiapi/testdata/realtime_1_day.xml')
    nodata = load_xml('./tests/fmiapi/testdata/nodata.xml')

    def describe_apikey():
        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_use_set_apikey_in_query(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.return_value = MockResponse(200, etree.tostring(daily_4_days))
            query = create_daily_query(datetime(2010, 1, 1, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2010, 1, 5, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone))

            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)

            result = fmiapi.get_daily_weather(query, None)
            assert 'fmi-apikey/{}/wfs?'.format(apikey) in mock_connection.request.call_args[0][1]
            verify_dataframe(result, EXPECTED_DAILY_4_DAYS)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_raise_invalid_apikey_exception_when_invalid_apikey_supplied(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.return_value = MockResponse(404, html_apikey_error, content_type='text/html')
            query = create_daily_query(datetime(2010, 1, 1, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2011, 1, 5, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone))

            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)

            with pytest.raises(InvalidApikeyException) as e:
                fmiapi.get_daily_weather(query, None)
            assert_equal('APIKEY', e.value.error_code)

    def describe_data_retrieval():

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_get_long_daily_weather(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(200, etree.tostring(daily_12_days)),
                                                       MockResponse(200, etree.tostring(daily_4_days))]
            query = create_daily_query(datetime(2000, 1, 1, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2001, 1, 16, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone))

            # simulate one long query with two short xml files which are fed to the request
            expected_df = copy.deepcopy(EXPECTED_DAILY_12_DAYS)
            for key in EXPECTED_DAILY_4_DAYS:
                expected_df[key] = expected_df[key] + EXPECTED_DAILY_4_DAYS[key]

            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)
            result = fmiapi.get_daily_weather(query, None)
            verify_dataframe(result, expected_df)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_get_realtime_weather_in_one_dataframe(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.return_value = MockResponse(200, etree.tostring(realtime_1_day))
            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)
            query = create_realtime_query(datetime(2012, 1, 13, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone),
                                          datetime(2012, 1, 14, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone))
            result = fmiapi.get_realtime_weather(query, None)
            verify_dataframe(result, EXPECTED_REALTIME_1_DAY)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_return_available_data_from_range_if_beginning_is_not_available(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(200, etree.tostring(nodata)), MockResponse(200, etree.tostring(realtime_1_day))]
            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)
            query = create_realtime_query(
                datetime(2012, 1, 1, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone),
                datetime(2012, 1, 14, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone))
            result = fmiapi.get_realtime_weather(query, None)
            verify_dataframe(result, EXPECTED_REALTIME_1_DAY)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_return_available_data_from_range_if_end_is_not_available(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(200, etree.tostring(nodata)),
                                                       MockResponse(200, etree.tostring(realtime_1_day)),
                                                       MockResponse(200, etree.tostring(nodata))]
            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)
            query = create_realtime_query(
                datetime(2012, 1, 8, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone),
                datetime(2012, 1, 16, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone))
            result = fmiapi.get_realtime_weather(query, None)
            verify_dataframe(result, EXPECTED_REALTIME_1_DAY)

    def describe_exceptions():
        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_raise_request_exception_when_request_count_exceeds_fmi_api_quota(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.return_value = MockResponse(409, html_querylimit_error, content_type='text/html')
            query = create_daily_query(datetime(2010, 1, 1, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2011, 1, 5, hour=2, minute=1, second=0, microsecond=0, tzinfo=timezone))
            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)

            with pytest.raises(QueryLimitException) as e:
                fmiapi.get_daily_weather(query, None)
            assert_equal('QUERYLIMIT', e.value.error_code)
            assert_equal('39', e.value.wait_time)
            assert_equal('seconds', e.value.wait_unit)

        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_raise_nodata_exception_if_range_of_data_is_empty(mock_httpconn):
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.side_effect = [MockResponse(200, etree.tostring(nodata))]
            fmiapi = FMIApi()
            apikey = '12345-12345'
            fmiapi.set_apikey(apikey)
            query = create_realtime_query(
                datetime(2008, 1, 13, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone),
                datetime(2008, 1, 14, hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone))

            with pytest.raises(NoDataException) as e:
                fmiapi.get_realtime_weather(query, None)
            assert_equal('NODATA', e.value.error_code)
