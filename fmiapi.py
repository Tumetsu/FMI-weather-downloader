from fmirequesthandler import FMIRequestHandler
import csv

class FMIApi():

    _api_key = ""
    _request_handler = None
    _DAILY_REQUEST_MAX_RANGE_HOURS = 8928
    _REALTIME_REQUEST_MAX_RANGE_HOURS = 168
    _PATH_TO_STATIONS_CSV = "stations.csv"
    stations = []

    def __init__(self):
        self._loadStationMetadata()

    def auth(self, api_key):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)

    def get_daily_weather(self, params, callbackFunction=None):
        return self._request_handler.request(params, max_range=self._DAILY_REQUEST_MAX_RANGE_HOURS,
                                             callbackFunction=callbackFunction)

    def get_realtime_weather(self, params, callbackFunction=None):
        return self._request_handler.request(params, max_range=self._REALTIME_REQUEST_MAX_RANGE_HOURS,
                                             callbackFunction=callbackFunction)

    def _loadStationMetadata(self):
        with open(self._PATH_TO_STATIONS_CSV, "r", encoding="utf8") as file:
            reader = csv.DictReader(file, ["Name", "FMISID", "LPNN", "WMO", "lat", "lon", "Altitude", "Group", "Since"],
                                    delimiter=";")
            for row in reader:
                self.stations.append(row)

    def getStationsList(self):
        return self.stations

    def getIndexOfPlace(self, placeName):
        for i in range(0, len(self.stations)):
            if self.stations[i]["Name"] == placeName:
                return i
        return -1





class ApiKeyException(Exception):
    message = "Please provide a valid API-key. Instructions to get one available on: " \
              "http://en.ilmatieteenlaitos.fi/open-data or" \
              "https://ilmatieteenlaitos.fi/avoin-data"
    errorCode = 0
    html = ""

