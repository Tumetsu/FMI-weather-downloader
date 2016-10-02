import math
import datetime
import copy
from fmiapi.fmirequest import FMIRequest
from fmiapi.fmierrors import RequestException


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
        for i, r in enumerate(requests):
            try:
                responses.append(self._do_request(r))
                if progress_callback is not None:
                    progress_callback(i, all_requests)
            except RequestException as e:
                # If result is 400, hope that the next request in batch will work. Raise other errors normally.
                # Handles case where beginning of a multipart request won't contain data
                # FIXME: Could be done in a way where after new lowerlimit is found, a new batch of requests is calculated instead of doing
                # FIXME: bunch of useless requests.
                if e.error_code != 400:
                    raise e
                if progress_callback is not None:
                    progress_callback(i, all_requests)

        return responses

    def _do_request(self, request):
        return self._FMI_request.get(request)

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
