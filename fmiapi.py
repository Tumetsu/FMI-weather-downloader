from fmirequesthandler import FMIRequestHandler

class FMIApi():

    _api_key = ""
    _request_handler = None
    _DAILY_REQUEST_MAX_RANGE_HOURS = 8928

    def auth(self, api_key):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)

    def get_daily_weather(self, params):
        return self._request_handler.request(params, max_range=self._DAILY_REQUEST_MAX_RANGE_HOURS)


class ApiKeyException(Exception):
    message = "Please provide a valid API-key. Instructions to get one available on: " \
              "http://en.ilmatieteenlaitos.fi/open-data or" \
              "https://ilmatieteenlaitos.fi/avoin-data"
    errorCode = 0
    html = ""
