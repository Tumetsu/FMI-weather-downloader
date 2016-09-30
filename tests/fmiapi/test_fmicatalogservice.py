from fmiapi.fmicatalogservice import get_station_metadata
from tests.fmiapi.testdata.expected_data import EXPECTED_LAMMI_CATALOG_METADATA
from tests.testUtils import *
from tests.fmiapi.commonmocks import *
from unittest import mock
from lxml import etree
from fmiapi.fmierrors import RequestException
import pytest


def describe_fmi_catalog_service():
    lammi_catalog_metadata = load_xml('./tests/fmiapi/testdata/lammi_catalog_metadata.xml')

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

    @mock.patch('http.client.HTTPConnection', spec=True)
    def should_throw_exception_when_request_fails(mock_httpconn):
        mock_connection = mock_httpconn.return_value
        mock_connection.getresponse.return_value = MockResponse(400, '')

        with pytest.raises(RequestException) as e:
            get_station_metadata('1234')
        assert_equal(400, e.value.error_code)