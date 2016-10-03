import csv
import json
import datetime
import re

from fmiapi.fmierrors import NoDataException
from fmiapi.fmirequesthandler import FMIRequestHandler
from fmiapi.fmixmlparser import FMIxmlParser
from fmiapi import fmicatalogservice


class FMIApi:
    """
    Provides a simple interface to interact with FMI API by providing basic functions to get
    data from FMI's open data service.
    """

    def __init__(self, api_key=''):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)
        self._DAILY_REQUEST_MAX_RANGE_HOURS = 8928
        self._REALTIME_REQUEST_MAX_RANGE_HOURS = 168
        self._PATH_TO_STATIONS_CSV = "data/stations.csv"
        self._PATH_TO_QUERY_METADATA = "data/supported_queries.json"
        self._stations = self._load_station_metadata()
        self._supported_queries = self._load_supported_queries_metadata()
        self._parser = FMIxmlParser()

    def set_apikey(self, api_key):
        self._api_key = api_key
        self._request_handler = FMIRequestHandler(self._api_key)

    def get_apikey(self):
        return self._api_key

    def get_data(self, params, callback_function=None, change_to_parsing=None):
        if params["storedquery_id"] == "fmi::observations::weather::daily::multipointcoverage":
            # Special logic for daily observations
            params['endtime'] += datetime.timedelta(days=1)  # add one day to end time to get final day into result too

        data = self._request_handler.request(params, max_timespan=params['max_hours_range'],
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
        stations = []
        with open(self._PATH_TO_STATIONS_CSV, "r", encoding="utf8") as file:
            reader = csv.DictReader(file, ["Name", "FMISID", "LPNN", "WMO", "lat", "lon", "Altitude", "Group", "Since"],
                                    delimiter=";")
            for row in reader:
                stations.append(row)
        return stations

    def _load_supported_queries_metadata(self):
        with open(self._PATH_TO_QUERY_METADATA, "r", encoding="utf8") as file:
            queries = json.load(file)
        return queries

    def get_stations(self):
        return self._stations

    def get_supported_queries(self):
        return self._supported_queries

    def get_catalogue_of_station(self, fmisid):
        # Add extra metadata for each dataset which are required for queries and translations
        # in short data which is not provided by catalogue service. See supported_queries.json
        datasets = fmicatalogservice.get_station_metadata(fmisid)
        augmented = []
        for ds in datasets:
            for sq in self._supported_queries:
                if re.search(sq['id'], ds['identifier']):
                    augmented.append({**ds, **sq})
                    break

        return augmented

    def get_index_of_station(self, place_name):
        for i in range(0, len(self._stations)):
            if self._stations[i]["Name"] == place_name:
                return i
        return -1
