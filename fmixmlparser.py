import pandas as pd
from io import StringIO
import lxml
from lxml import etree
from fmierrors import *

class FMIxmlParser:

    _GMLCOV = {"gmlcov" : "http://www.opengis.net/gmlcov/1.0"}
    _GML = {"gml" : "http://www.opengis.net/gml/3.2"}
    _SWE = {"swe" : "http://www.opengis.net/swe/2.0"}

    _field_names = []
    _dataframes = []

    def __init__(self):
        self._field_names = []
        self._dataframes = []

    def parse(self, xml_data_list):
        try:
            for item in xml_data_list:
                #locationName = item[0].find(".//_GML:name", namespaces=self._GML).text
                df = self._parse_datapoints(item)
                df = df[:-2]
                self._dataframes.append(df)
                #TODO: CALLBACK KERTOMAAN ETENEMISESTÄ?

            totaldf = self._join_dataframes()
            totaldf = self._clean_na_values(totaldf)
            return totaldf
        except (IndexError, ValueError) as e:
            raise NoDataException()

    def _join_dataframes(self):
        return pd.concat(self._dataframes, ignore_index=True)

    def _parse_datapoints(self, xmlData):
        df_positionTime = self._parse_positions(xmlData)
        df_observations = self._parse_measurementdata(xmlData)
        df_observations = self._combine_time_and_observation(df_observations, df_positionTime)
        return df_observations

    def _parse_positions(self, xmlData,):
        positions = xmlData[0].find(".//gmlcov:positions", namespaces=self._GMLCOV).text
        return pd.read_csv(StringIO(positions), delim_whitespace=True, names=["lat", "long", "time"])

    def _parse_measurementdata(self, xmlData):
        #get field names available in file
        fields = xmlData[0].findall(".//swe:field", namespaces=self._SWE)
        self._field_names = []
        for f in fields:
            self._field_names.append(f.get("name"))

        #get actual meaurement data
        observed = xmlData[0].find(".//gml:doubleOrNilReasonTupleList", namespaces=self._GML).text
        df_observations = pd.read_csv(StringIO(observed), delim_whitespace=True, names=self._field_names)
        df_observations = df_observations.applymap(str).replace(r'\.',',',regex=True)    #decimal dot to comma

        return df_observations

    def _combine_time_and_observation(self, df_observations, df_positionTime):
        df_observations["time"] = df_positionTime["time"]
        df_observations["time"] = pd.to_datetime(df_observations["time"], unit="s")
        self._field_names.insert(0, "time")
        df_observations = df_observations[self._field_names]
        return df_observations

    def _clean_na_values(self, df):
        df = df.replace('nan', pd.np.nan)
        df = df.dropna(axis=1, how='all')
        df = df.replace(pd.np.nan, "")
        return df

    def clear(self):
        self._dataframes = []
        self._field_names = []

