import csv
from fmiapi.fmirequesthandler import FMIRequestHandler


class FMIApi:
    """
    Provides a simple interface to interact with FMI API by providing basic functions to get
    data from FMI's open data service.
    """

    def __init__(self):
        self._api_key = ""
        self._request_handler = None
        self._DAILY_REQUEST_MAX_RANGE_HOURS = 8928
        self._REALTIME_REQUEST_MAX_RANGE_HOURS = 168
        self._PATH_TO_STATIONS_CSV = "stations.csv"
        self._stations = []
        self._load_station_metadata()

    def set_apikey(self, api_key):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)

    def get_daily_weather(self, params, callback_function=None):
        return self._request_handler.request(params, max_timespan=self._DAILY_REQUEST_MAX_RANGE_HOURS,
                                             progress_callback=callback_function)

    def get_realtime_weather(self, params, callback_function=None):
        return self._request_handler.request(params, max_timespan=self._REALTIME_REQUEST_MAX_RANGE_HOURS,
                                             progress_callback=callback_function)

    def _load_station_metadata(self):
        """ FMI apparently didn't provide an API-endpoint to get list of all the stations. For now, we load the
        required station information from CSV-file. Change to a api-endpoint if one becomes (or is already?) available.
        """
        with open(self._PATH_TO_STATIONS_CSV, "r", encoding="utf8") as file:
            reader = csv.DictReader(file, ["Name", "FMISID", "LPNN", "WMO", "lat", "lon", "Altitude", "Group", "Since"],
                                    delimiter=";")
            for row in reader:
                self._stations.append(row)

    def get_stations(self):
        return self._stations

    def get_index_of_station(self, place_name):
        for i in range(0, len(self._stations)):
            if self._stations[i]["Name"] == place_name:
                return i
        return -1


class ApiKeyException(Exception):
    message = "Please provide a valid API-key. Instructions to get one available on: " \
              "http://en.ilmatieteenlaitos.fi/open-data or" \
              "https://ilmatieteenlaitos.fi/avoin-data"
    errorCode = 0
    html = ""
