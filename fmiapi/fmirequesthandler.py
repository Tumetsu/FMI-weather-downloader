import math
import datetime
import copy
from fmiapi.fmirequest import FMIRequest


class FMIRequestHandler:
    """
    This class takes a data request and splits it to multiple http-requests if required and
    does the request by using FMIRequest class.
    """

    def __init__(self, api_key):
        self._api_key = api_key
        self._FMI_request = FMIRequest(self._api_key)
        self._callbackFunction = None

    def request(self, params, max_timespan, progress_callback=None):
        requests = self._divide_to_multiple_requests(params, max_timespan)
        return self._execute_requests(requests, progress_callback)

    def _execute_requests(self, requests, progress_callback):
        all_requests = len(requests)
        responses = []
        count = 0
        for r in requests:
            responses.append(self._do_request(r))
            count += 1
            if progress_callback is not None:
                progress_callback(count, all_requests)
        return responses

    def _do_request(self, request):
        return self._FMI_request.get(request)

    @staticmethod
    def _required_requests_count(start_time, end_time, max_range):
        time_diff = end_time - start_time
        time_diff_in_hours = time_diff.days*24
        return math.ceil(time_diff_in_hours / max_range)

    @staticmethod
    def _divide_to_multiple_requests(params, max_timespan):
        requests = []
        done = False
        i = 0
        while not done:
            request_params = copy.copy(params)
            request_params["starttime"] += datetime.timedelta(hours=max_timespan)*i
            request_params["endtime"] = request_params["starttime"] + datetime.timedelta(hours=max_timespan-1)
            requests.append(request_params)

            if request_params["endtime"] > params["endtime"]:
                done = True
                request_params["endtime"] = params["endtime"]
            i += 1
        return requests
