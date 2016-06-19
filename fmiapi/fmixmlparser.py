from io import StringIO
import pandas as pd
from fmiapi.fmierrors import *


class FMIxmlParser:
    """
    Ad-hoc class to parse multipoint-coverage xml supplied from FMI-service and convert the multipoint-coverage
    values to a single Pandas dataframe. Class is not designed for general use and extracts only relevant data
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
            for item in xml_data_list:
                location_name = self._get_location_name(item)
                df = self._parse_datapoints(item)
                df = df[:-2]
                self._dataframes.append(df)
                # TODO: Callback to notify about progress?

            totaldf = self._join_dataframes(self._dataframes)
            totaldf = self._clean_na_values(totaldf)
            totaldf["place"] = location_name
            return totaldf
        except (IndexError, ValueError):
            raise NoDataException()

    @staticmethod
    def _get_location_name(item):
        return item[0].find(".//gml:name", namespaces=FMIxmlParser._GML).text

    @staticmethod
    def _join_dataframes(dataframes) -> pd.DataFrame:
        return pd.concat(dataframes, ignore_index=True)

    def _parse_datapoints(self, xml_data):
        df_position_time = self._parse_positions(xml_data)
        df_observations = self._parse_measurementdata(xml_data)
        df_observations = self._combine_time_and_observation(df_observations, df_position_time)
        return df_observations

    def _parse_positions(self, xml_data):
        positions = xml_data[0].find(".//gmlcov:positions", namespaces=self._GMLCOV).text
        # TODO: Replace Pandas with more lightweight implementation
        return pd.read_csv(StringIO(positions), delim_whitespace=True, names=["lat", "long", "time"])

    def _parse_measurementdata(self, xml_data):
        # get field names available in file
        fields = xml_data[0].findall(".//swe:field", namespaces=self._SWE)
        self._field_names = []
        for f in fields:
            self._field_names.append(f.get("name"))

        # get actual measurement data
        observed = xml_data[0].find(".//gml:doubleOrNilReasonTupleList", namespaces=self._GML).text
        # TODO: Replace Pandas with more lightweight implementation
        df_observations = pd.read_csv(StringIO(observed), delim_whitespace=True, names=self._field_names)
        df_observations = df_observations.applymap(str).replace(r'\.', ',', regex=True)  # decimal dot to comma
        return df_observations

    def _combine_time_and_observation(self, df_observations, df_position_time):
        # TODO: Do conversion from unix timestamp to regular date with something else than Pandas
        df_observations["time"] = df_position_time["time"]
        df_observations["time"] = pd.to_datetime(df_observations["time"], unit="s")
        self._field_names.insert(0, "time")
        df_observations = df_observations[self._field_names]
        return df_observations

    @staticmethod
    def _clean_na_values(df):
        df = df.replace('nan', pd.np.nan)
        df = df.dropna(axis=1, how='all')
        df = df.replace(pd.np.nan, "")
        return df

    def clear(self):
        self._dataframes = []
        self._field_names = []
