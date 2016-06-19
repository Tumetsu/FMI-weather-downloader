from fmiapi.fmierrors import *
import datetime
from collections import OrderedDict

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
        try:
            location_name = ""
            dataframe = None
            for item in xml_data_list:
                location_name = self._get_location_name(item)
                df = self._parse_datapoints(item)
                dataframe = self._join_data(dataframe, df)
                # TODO: Callback to notify about progress?

            dataframe["place"] = [location_name] * len(dataframe['time'])
            return dataframe
        except (IndexError, ValueError):
            raise NoDataException()

    def _join_data(self, existing, df):
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

    def _timestamp2datestr(self, timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

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
                result[headers[h]].append(observed[i + h])
        return result

    def _map_times_to_observations(self, df_observations, df_position_time):
        combined = OrderedDict()
        combined["time"] = df_position_time["time"]
        combined.update(df_observations)
        return combined

    # TODO: Might be needed later
    def _clean_na_values(self, df):
        pass
