import lxml
import http.client
import urllib.request
from lxml import etree
import pandas as pd
from io import StringIO
import datetime
import urllib.parse

class FMI_request():

    url = "data.fmi.fi"
    apikey = "4d7bcd64-01af-4dbb-8a43-404e97b8c2cd"
    headers =  {"Content-type": "text/xml"}
    connection = None

    xmlns = {"xmlns" : "http://www.opengis.net/ows/1.1"}


    def __init__(self):
        self.connection = http.client.HTTPConnection(self.url)

    def get(self, params):
        self.connection.request("GET", "/fmi-apikey/" + self.apikey + "/wfs?" + urllib.parse.urlencode(params),
                                headers=self.headers)
        response = self.connection.getresponse()
        print(response.status)
        if response.status == 200:
            data = response.read()
            return etree.XML(data)
        else:
            print(response.read())
            self._getErrorReason(response)
            raise RequestException(self._getErrorReason(response), response.status)

    def _getErrorReason(self, response):
        if response.getheader("Content-Type") == "text/html":
            raise RequestException("Error in html", response.status, html=response.read())

        elif response.getheader("Content-Type") == "text/xml":
            print("asdasd")
            print(response.read())
            xml = etree.XML(response.read())
            raise RequestException(xml.find(".//xmlns:ExceptionText", namespaces=self.xmlns).text, response.status)



class ParseXML:
    gmlcov = {"gmlcov" : "http://www.opengis.net/gmlcov/1.0"}
    gml = {"gml" : "http://www.opengis.net/gml/3.2"}
    swe = {"swe" : "http://www.opengis.net/swe/2.0"}

    fieldNames = []
    df_positionTime = None
    df_observations = None

    def parse(self, xmlData):
        print(xmlData[0].tag)
        locationName = xmlData[0].find(".//gml:name", namespaces=self.gml).text
        print(locationName)
        self._parseDataPoints(xmlData)

    def _parseDataPoints(self, xmlData):
        self.df_positionTime = self._parsePositions(xmlData)
        self.df_observations = self._parseMeasurementData(xmlData)
        self.df_observations = self._combineTimeWithObservation(self.df_observations, self.df_positionTime)
        #save
        self.df_observations.to_csv("file.csv", sep=",", date_format="%d.%m.%Y", index=False)

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
        return df_observations

    def _combineTimeWithObservation(self, df_observations, df_positionTime):
        df_observations["time"] = df_positionTime["time"]
        df_observations["time"] = pd.to_datetime(df_observations["time"], unit="s")
        self.fieldNames.insert(0, "time")
        df_observations = self.df_observations[self.fieldNames]
        return df_observations



class RequestException(Exception):
    message = "ERROR in "
    errorCode = 0
    html = ""

    def __init__(self, text, errorCode, html = ""):
        self.message = text
        self.errorCode = errorCode
        self.html = html
        print(html)













if __name__ == '__main__':

    query = "/wfs?request=getFeature&storedquery_id=fmi::observations::" \
            "weather::daily::multipointcoverage&place=Lammi&timestep=1"
    FMIrequest = FMI_request()

    try:
        params = { "request" : "getFeature",
                   "storedquery_id" : "fmi::observations::weather::daily::multipointcoverage",
                   "place" : "Lammi",
                   "timestep" : 1
        }

        dataInXml = FMIrequest.get(params)
        print(etree.tostring(dataInXml))
        parser = ParseXML()
        parser.parse(dataInXml)

    except RequestException as e:
        print(e.message)

