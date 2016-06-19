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

    def request(self, params, max_range, progress_callback=None):
        requests = self._prepare_requests(params, max_range)
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

    def _prepare_requests(self, params, max_range):
        required_requests = self._required_requests_count(params["starttime"], params["endtime"], max_range)
        if required_requests == 1:
            return [params]
        else:
            return self._divide_to_multiple_requests(params, required_requests)

    def _do_request(self, request):
        return self._FMI_request.get(request)

    @staticmethod
    def _required_requests_count(start_time, end_time, max_range):
        time_diff = end_time - start_time
        time_diff_in_hours = time_diff.days*24
        return math.ceil(time_diff_in_hours / max_range)

    @staticmethod
    def _divide_to_multiple_requests(params, amount):
        time_diff = params["endtime"] - params["starttime"]
        time_diff_in_days = time_diff.days
        time_delta = math.ceil(time_diff_in_days/amount)

        requests = []
        for i in range(0, amount):
            new_request_params = copy.copy(params)
            offset = time_delta*i
            new_date = params["starttime"] + datetime.timedelta(days=offset)
            new_request_params["starttime"] = new_date.strftime("%Y-%m-%dT00:00:00Z")

            new_end_date = new_date + datetime.timedelta(days=time_delta)
            new_request_params["endtime"] = new_end_date.strftime("%Y-%m-%dT00:00:00Z")
            requests.append(new_request_params)
        return requests
