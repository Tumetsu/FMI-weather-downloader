import math
import datetime
import copy
from fmirequest import FMIRequest
class FMIRequestHandler():



    def __init__(self, api_key):
        self._api_key = api_key
        self._FMI_request = FMIRequest(self._api_key)
        self._callbackFunction = None

    def request(self, params, max_range, callbackFunction=None):
        requests = self._prepare_requests(params, max_range)
        responses = []
        count = 0
        all = len(requests)

        for r in requests:
            responses.append(self._do_request(r))
            count += 1

            if callbackFunction is not None:
                callbackFunction(count, all)

        return responses


    def _prepare_requests(self, params, max_range):
        required_requests = self._how_many_requests_needed(params["starttime"], params["endtime"], max_range)
        print(required_requests)
        if required_requests == 1:
            return [params]
        else:
            #pilko osiin
            return self._divide_to_multiple_requests(params, required_requests)



    def _do_request(self, request):
        return self._FMI_request.get(request)


    def _how_many_requests_needed(self, start_time, end_time, max_range):
        time_diff = end_time - start_time
        time_diff_in_hours = time_diff.days*24
        return math.ceil(time_diff_in_hours / max_range)


    def _divide_to_multiple_requests(self, params, amount):
        time_diff = params["endtime"] - params["starttime"]
        time_diff_in_days = time_diff.days
        time_delta = math.ceil(time_diff_in_days/(amount)) #days

        requests = []
        for i in range(0, amount):
            new_request_params = copy.copy(params)
            diff = time_delta*i
            new_date = params["starttime"] + datetime.timedelta(days=diff)
            new_request_params["starttime"] = new_date.strftime("%Y-%m-%dT00:00:00Z")

            new_end_date = new_date + datetime.timedelta(days=time_delta)
            new_request_params["endtime"] = new_end_date.strftime("%Y-%m-%dT00:00:00Z")
            requests.append(new_request_params)
        return requests


    def _do_parallel_request(self):
        pass

