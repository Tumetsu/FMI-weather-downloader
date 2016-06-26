import csv
import datetime

from fmiapi.fmierrors import NoDataException
from fmiapi.fmirequesthandler import FMIRequestHandler
from fmiapi.fmixmlparser import FMIxmlParser


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
        self._parser = FMIxmlParser()

    def set_apikey(self, api_key):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)

    def get_apikey(self):
        return self._api_key

    def get_daily_weather(self, params, callback_function=None, change_to_parsing=None):
        params['endtime'] += datetime.timedelta(days=1) # add one day to end time to get final day into result too
        data = self._request_handler.request(params, max_timespan=self._DAILY_REQUEST_MAX_RANGE_HOURS,
                                             progress_callback=callback_function)

        # Notify ui that moving to parsing phase
        if change_to_parsing is not None:
            change_to_parsing()

        try:
            return self._parser.parse(data, progress_callback=callback_function)
        except NoDataException:
            # Augment date data to exception and raise it again
            raise NoDataException(starttime=params['starttime'], endtime=params['endtime'])

    def get_realtime_weather(self, params, callback_function=None, change_to_parsing=None):
        data = self._request_handler.request(params, max_timespan=self._REALTIME_REQUEST_MAX_RANGE_HOURS,
                                             progress_callback=callback_function)

        # Notify ui that moving to parsing phase
        if change_to_parsing is not None:
            change_to_parsing()

        try:
            return self._parser.parse(data, progress_callback=callback_function)
        except NoDataException:
            # Augment date data to exception and raise it again
            raise NoDataException(starttime=params['starttime'], endtime=params['endtime'])

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

