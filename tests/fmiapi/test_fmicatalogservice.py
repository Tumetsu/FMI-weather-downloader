from fmiapi.fmicatalogservice import get_station_metadata
from tests.fmiapi.testdata.expected_data import EXPECTED_LAMMI_CATALOG_METADATA
from tests.testUtils import *
from tests.fmiapi.commonmocks import *
from unittest import mock
from lxml import etree
from fmiapi.fmierrors import RequestException, NoDataSetsException
import pytest


def describe_fmi_catalog_service():
    lammi_catalog_metadata = load_xml('./tests/fmiapi/testdata/lammi_catalog_metadata.xml')
    search_exception_response = load_xml('./tests/fmiapi/testdata/search_exception_response.xml')

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_do_request_to_catalog_service_with_provided_query_params_and_return_data(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(200, etree.tostring(lammi_catalog_metadata))

        result = get_station_metadata('1234')
        assert_equal(1, mock_connection.getresponse.call_count)

        for i, record in enumerate(EXPECTED_LAMMI_CATALOG_METADATA):
            assert_equal(result[i]['latitude'], record['latitude'])
            assert_equal(result[i]['longitude'], record['longitude'])
            assert_equal(result[i]['link'], record['link'])
            assert_equal(result[i]['identifier'], record['identifier'])
            assert_equal(result[i]['title_fi'], record['title_fi'])
            assert result[i]['starttime'] == record['starttime']
            assert result[i]['endtime'] == record['endtime']

    def describe_fmi_returns_search_exception():
        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_retry_request_3_more_times_before_giving_up_if_search_did_not_return_results(mock_httpconn):
            # Looks like occasionally FMI api returns Java exception response when doing completely valid
            # searches... We should handle it properly and just try again couple of times and hope it goes away.
            mock_connection = mock_httpconn.return_value
            mock_connection.getresponse.return_value = MockResponse(200, etree.tostring(search_exception_response))

            with pytest.raises(RequestException) as e:
                get_station_metadata('1234')
            assert_equal('METADATA_RETRIEVAL', e.value.error_code)
            assert_equal(4, mock_connection.getresponse.call_count)  # Should have tried in total 4 times


        @mock.patch('http.client.HTTPConnection', spec=True)
        def should_return_proper_data_after_first_failed_request(mock_httpconn):
            # Looks like occasionally FMI api returns Java exception response when doing completely valid
            # searches... We should handle it properly and just try again couple of times and hope it goes away.
            mock_connection = mock_httpconn.return_value

            # Mocked responses. Note that the first one is the exception response
            mock_connection.getresponse.side_effect = [
                MockResponse(200, etree.tostring(search_exception_response)),
                MockResponse(200, etree.tostring(lammi_catalog_metadata))
            ]

            result = get_station_metadata('1234')
            assert_equal(2, mock_connection.getresponse.call_count)

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_throw_exception_when_request_fails(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(400, '')

        with pytest.raises(RequestException) as e:
            get_station_metadata('1234')
        assert_equal('METADATA_RETRIEVAL', e.value.error_code)

    @mock.patch('fmiapi.fmicatalogservice._parse_data', spec=True)
    def should_throw_exception_when_request_returns_empty_list(mock_parse):
        mock_parse.return_value = []

        with pytest.raises(NoDataSetsException) as e:
            get_station_metadata('1234')
        assert_equal('NODATASETS', e.value.error_code)