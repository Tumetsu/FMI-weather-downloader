from fmiapi.fmirequesthandler import FMIRequestHandler
from datetime import datetime
from tests.testUtils import *
from unittest import mock
from unittest.mock import call
from fmiapi.fmierrors import RequestException
import pytz
import pytest
timezone = pytz.timezone('Europe/Helsinki')

def describe_fmi_request_handler():
    fmi_handler = FMIRequestHandler('apikey')
    _DAILY_REQUEST_MAX_RANGE_HOURS = 8928
    _REALTIME_REQUEST_MAX_RANGE_HOURS = 168

    @mock.patch('fmiapi.fmirequesthandler.FMIRequest', spec=True)
    def should_get_year_in_one_request(mock_fmirequest):
        query = {'request': 'getFeature',
                 'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage',
                 'fmisid': '1234',
                 'starttime': datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                 'endtime': datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone)
                 }

        expected = {'starttime': datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                    'endtime': datetime(2011, 1, 5, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                    'fmisid': '1234',
                    'request': 'getFeature',
                    'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage'
                    }

        mock_instance = mock_fmirequest.return_value
        mock_instance.get.return_value = 'data'

        handler = FMIRequestHandler('apikey')
        result = handler.request(query, max_timespan=_DAILY_REQUEST_MAX_RANGE_HOURS, progress_callback=None)

        mock_instance.get.assert_has_calls([call(expected)])
        assert_equal(1, mock_instance.get.call_count)
        assert_equal(1, len(result))

    @mock.patch('fmiapi.fmirequesthandler.FMIRequest', spec=True)
    def should_call_fmirequest_in_two_parts_for_372_day_time_span(mock_fmirequest):
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 23, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))

        expected = [create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2011, 1, 8, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone)),
                    create_daily_query(datetime(2011, 1, 8, hour=0, minute=2, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2011, 1, 23, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))]

        expected_calls = [call(expected[0]), call(expected[1])]
        mock_instance = mock_fmirequest.return_value
        mock_instance.get.return_value = 'data'

        handler = FMIRequestHandler('apikey')
        result = handler.request(query, max_timespan=_DAILY_REQUEST_MAX_RANGE_HOURS, progress_callback=None)

        mock_instance.get.assert_has_calls(expected_calls)
        assert_equal(2, mock_instance.get.call_count)
        assert_equal(2, len(result))

    @mock.patch('fmiapi.fmirequesthandler.FMIRequest', spec=True)
    def should_return_available_data_if_first_part_of_request_does_not_exist(mock_fmirequest):
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 23, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))

        expected = [create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                       datetime(2011, 1, 8, hour=0, minute=1, second=0, microsecond=0,
                                                tzinfo=timezone))]

        expected_calls = [call(expected[0])]
        # On first request throw exception with code 400, then return return value normally
        # Simulates query where first part is not available, but second is
        mock_fmirequest.return_value.get.side_effect = [RequestException('error', 400), mock.DEFAULT]
        mock_instance = mock_fmirequest.return_value
        mock_instance.get.return_value = 'data'

        handler = FMIRequestHandler('apikey')
        result = handler.request(query, max_timespan=_DAILY_REQUEST_MAX_RANGE_HOURS, progress_callback=None)

        mock_instance.get.assert_has_calls(expected_calls)
        assert_equal(2, mock_instance.get.call_count)
        assert_equal(1, len(result))

    @mock.patch('fmiapi.fmirequesthandler.FMIRequest', spec=True)
    def should_return_empty_list_if_only_400_errors(mock_fmirequest):
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 23, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone))

        mock_fmirequest.return_value.get.side_effect = [RequestException('error', 400), RequestException('error', 400)]
        mock_instance = mock_fmirequest.return_value
        mock_instance.get.return_value = 'data'

        handler = FMIRequestHandler('apikey')
        result = handler.request(query, max_timespan=_DAILY_REQUEST_MAX_RANGE_HOURS, progress_callback=None)
        assert_equal(2, mock_instance.get.call_count)
        assert_equal(0, len(result))

    @mock.patch('fmiapi.fmirequesthandler.FMIRequest', spec=True)
    def should_raise_error_normally_if_error_code_is_something_else_than_400(mock_fmirequest):
        query = create_daily_query(datetime(2010, 1, 1, hour=0, minute=1, second=0, microsecond=0, tzinfo=timezone),
                                   datetime(2011, 1, 23, hour=0, minute=1, second=0, microsecond=0,
                                            tzinfo=timezone))

        mock_fmirequest.return_value.get.side_effect = [RequestException('error', 'othererror'),
                                                        RequestException('error', 400)]
        mock_instance = mock_fmirequest.return_value
        mock_instance.get.return_value = 'data'

        handler = FMIRequestHandler('apikey')
        with pytest.raises(RequestException) as e:
            handler.request(query, max_timespan=_DAILY_REQUEST_MAX_RANGE_HOURS, progress_callback=None)

        assert_equal('othererror', e.value.error_code)
        assert_equal(1, mock_instance.get.call_count)
