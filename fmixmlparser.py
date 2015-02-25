import pandas as pd
from io import StringIO
import lxml
from lxml import etree
from fmierrors import *

class FMIxmlParser:

    gmlcov = {"gmlcov" : "http://www.opengis.net/gmlcov/1.0"}
    gml = {"gml" : "http://www.opengis.net/gml/3.2"}
    swe = {"swe" : "http://www.opengis.net/swe/2.0"}

    fieldNames = []
    df_positionTime = None
    df_observations = None
    dataframes = []

    def __init__(self):
        print("PARSERI TEHTY")
        self.fieldNames = []
        self.df_positionTime = None
        self.df_observations = None
        self.dataframes = []

    def parse(self, xmlDataList):
        try:

            for item in xmlDataList:

                locationName = item[0].find(".//gml:name", namespaces=self.gml).text
                print(locationName)
                df = self._parseDataPoints(item)
                df = df[:-2]
                print(df)
                self.dataframes.append(df)

            print (len(self.dataframes))
            totaldf = self._joinDataframes()
            return totaldf
        except (IndexError, ValueError) as e:
            raise NoDataException()


    def _joinDataframes(self):
        return pd.concat(self.dataframes, ignore_index=True)




    def _parseDataPoints(self, xmlData):
        df_positionTime = self._parsePositions(xmlData)
        df_observations = self._parseMeasurementData(xmlData)
        df_observations = self._combineTimeWithObservation(df_observations, df_positionTime)
        return df_observations




    def _parsePositions(self, xmlData,):
        positions = xmlData[0].find(".//gmlcov:positions", namespaces=self.gmlcov).text
        return pd.read_csv(StringIO(positions), delim_whitespace=True, names=["lat", "long", "time"])

    def _parseMeasurementData(self, xmlData):
        #get field names available in file
        fields = xmlData[0].findall(".//swe:field", namespaces=self.swe)
        self.fieldNames = []
        for f in fields:
            self.fieldNames.append(f.get("name"))

        #get actual meaurement data
        observed = xmlData[0].find(".//gml:doubleOrNilReasonTupleList", namespaces=self.gml).text
        df_observations = pd.read_csv(StringIO(observed), delim_whitespace=True, names=self.fieldNames)
        df_observations = df_observations.applymap(str).replace(r'\.',',',regex=True)    #decimal dot to comma
        return df_observations

    def _combineTimeWithObservation(self, df_observations, df_positionTime):
        df_observations["time"] = df_positionTime["time"]
        df_observations["time"] = pd.to_datetime(df_observations["time"], unit="s")
        self.fieldNames.insert(0, "time")
        df_observations = df_observations[self.fieldNames]
        return df_observations

    def clear(self):
        self.dataframes = []
        self.fieldNames = []
        self.df_positionTime = None
        self.df_observations = None

