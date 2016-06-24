from fmiapi.fmierrors import *
import datetime
from collections import OrderedDict
import math


class FMIxmlParser:
    """
    Ad-hoc class to parse multipoint-coverage xml supplied from FMI-service and convert the multipoint-coverage
    values to dict of lists. Class is not designed for general use and extracts only relevant data
    for this use case. More general approach might be nice for extending the application.
    """

    _GMLCOV = {"gmlcov": "http://www.opengis.net/gmlcov/1.0"}
    _GML = {"gml": "http://www.opengis.net/gml/3.2"}
    _SWE = {"swe": "http://www.opengis.net/swe/2.0"}

    def __init__(self):
        self._field_names = []
        self._dataframes = []

    def parse(self, xml_data_list):
        location_name = ""
        dataframe = None
        no_data_cases = 0
        for item in xml_data_list:
            try:
                location_name = self._get_location_name(item)
                df = self._parse_datapoints(item)
                dataframe = self._join_data(dataframe, df)
                # TODO: Callback to notify about progress?
            except (IndexError, ValueError):
                no_data_cases += 1

        # If request did not produce anything, throw exception. Otherwise return gotten data.
        if no_data_cases == len(xml_data_list):
            raise NoDataException()

        dataframe["place"] = [location_name] * len(dataframe['time'])
        dataframe = self._clean_na_values(dataframe)
        return dataframe

    @staticmethod
    def _join_data(existing, df):
        if existing is None:
            return df
        else:
            for key in df:
                existing[key] = existing[key] + df[key]
            return existing

    @staticmethod
    def _get_location_name(item):
        return item[0].find(".//gml:name", namespaces=FMIxmlParser._GML).text

    def _parse_datapoints(self, xml_data):
        df_position_time = self._parse_positions(xml_data)
        df_observations = self._parse_measurementdata(xml_data)
        df_observations = self._map_times_to_observations(df_observations, df_position_time)
        return df_observations

    def _parse_positions(self, xml_data):
        positions = xml_data[0].find(".//gmlcov:positions", namespaces=self._GMLCOV).text
        positions = positions.split()

        result = OrderedDict({'time': [], 'lat': [], 'long': []})

        for i in range(0, len(positions), 3):
            result['time'].append(self._timestamp2datestr(positions[i + 2]))
            result['long'].append(positions[i+1])
            result['lat'].append(positions[i])

        return result

    @staticmethod
    def _timestamp2datestr(timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%dT%H:%M')

    def _parse_measurementdata(self, xml_data):
        # get field names available in file
        fields = xml_data[0].findall(".//swe:field", namespaces=self._SWE)
        result = OrderedDict()
        headers = []
        for f in fields:
            headers.append(f.get("name"))
            result[f.get("name")] = []

        # get actual measurement data
        observed = xml_data[0].find(".//gml:doubleOrNilReasonTupleList", namespaces=self._GML).text
        observed = observed.split()

        for i in range(0, len(observed), len(headers)):
            for h in range(0, len(headers)):
                result[headers[h]].append(float(observed[i + h]))
        return result

    @staticmethod
    def _map_times_to_observations(df_observations, df_position_time):
        combined = OrderedDict()
        combined["time"] = df_position_time["time"]
        combined.update(df_observations)
        return combined

    @staticmethod
    def _clean_na_values(df):
        mark_for_removal = []
        for key, column in df.items():
            nan_count = 0
            for i in range(0, len(column)):
                if type(column[i]) is float and math.isnan(column[i]):
                    nan_count += 1
                    column[i] = 'NaN'
            if nan_count == len(column):
                mark_for_removal.append(key)

        for rm in mark_for_removal:
            df.pop(rm, None)
        return df
