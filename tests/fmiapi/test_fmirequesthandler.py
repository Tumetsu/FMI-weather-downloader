from fmiapi.fmirequesthandler import FMIRequestHandler
from datetime import datetime
from tests.testUtils import *




class TestFMIRequestHandler():

    def setup(self):
        self.fmi_handler = FMIRequestHandler('apikey')
        self._DAILY_REQUEST_MAX_RANGE_HOURS = 8928
        self._REALTIME_REQUEST_MAX_RANGE_HOURS = 168

    def should_get_year_in_one_request(self):
        start_time = datetime.strptime('2010-01-01T00:01', '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime('2010-01-05T00:01', '%Y-%m-%dT%H:%M')
        expected_count = 1
        count = self.fmi_handler._required_requests_count(start_time, end_time, self._DAILY_REQUEST_MAX_RANGE_HOURS)
        assertEqual(expected_count, count)

    def should_count_2_request_for_over_372_day_time_span(self):
        start_time = datetime.strptime('2010-01-01T00:01', '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime('2011-01-09T00:01', '%Y-%m-%dT%H:%M')
        expected_count = 2
        count = self.fmi_handler._required_requests_count(start_time, end_time, self._DAILY_REQUEST_MAX_RANGE_HOURS)
        assertEqual(expected_count, count)

    def should_prepare_2_requests_for_over_372_day_time_span(self):
        start_time = datetime.strptime('2010-01-01T00:01', '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime('2011-01-23T00:01', '%Y-%m-%dT%H:%M')
        expected_count = 2
        requests = self.fmi_handler._divide_to_multiple_requests({"starttime": start_time,
                                                                  "endtime": end_time},
                                                                 self._DAILY_REQUEST_MAX_RANGE_HOURS)
        assertEqual(expected_count, len(requests))
        assertEqual('2010-01-01', requests[0]["starttime"].strftime('%Y-%m-%d'))
        assertEqual('2011-01-07', requests[0]["endtime"].strftime('%Y-%m-%d'))
        assertEqual('2011-01-08', requests[1]["starttime"].strftime('%Y-%m-%d'))
        assertEqual('2011-01-23', requests[1]["endtime"].strftime('%Y-%m-%d'))
