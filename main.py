import lxml
import http.client
import urllib.request
from lxml import etree
import csv

class FMI_request():

    url = "data.fmi.fi"
    apikey = "4d7bcd64-01af-4dbb-8a43-404e97b8c2cd"
    headers =  {"Content-type": "text/xml"}
    connection = None

    query1 = "/wfs?request=listStoredQueries"


    def __init__(self):
        self.connection = http.client.HTTPConnection(self.url)

    def get(self, query):
        self.connection.request("GET", "/fmi-apikey/" + self.apikey + query,
                                headers=self.headers)
        response = self.connection.getresponse()
        print(response.status)
        if response.status == 200:
            data = response.read()
            return etree.XML(data)

        else:
            raise RequestException("Couldn't connect to server. Http-error: " + str(response.status) + " " + response.reason)


#luokka muuntamaan xml-tietorakenteeksi
class XmlToClass:
    headers =  {"Content-type": "text/xml"}

    def transform(self, xmldata):

        parsedData = {"location" : "", "data": []}
        for item in xmldata:
            #print(str(item.findall(".//", namespaces={"gml" : "http://www.opengis.net/gml/3.2"})))
            parsedData["location"] = item.find(".//gml:name", namespaces={"gml" : "http://www.opengis.net/gml/3.2"}).text
            parsedData["data"].append(self._getMeasurements(item))

        return parsedData



    def _getMeasurements(self, member):
        urlToInfo = member.find(".//om:observedProperty", namespaces={"om" : "http://www.opengis.net/om/2.0"}).get("{http://www.w3.org/1999/xlink}href")
        request = urllib.request.Request(urlToInfo, headers=self.headers)
        xml = etree.XML(urllib.request.urlopen(request).read())
        label = xml.find('xmlns:label', namespaces={"xmlns" : "http://inspire.ec.europa.eu/schemas/omop/2.9"}).text
        unit = xml.find('xmlns:uom', namespaces={"xmlns" : "http://inspire.ec.europa.eu/schemas/omop/2.9"}).get("uom")
        statFunction = xml.find('.//xmlns:statisticalFunction', namespaces={"xmlns" : "http://inspire.ec.europa.eu/schemas/omop/2.9"}).text
        aggregationTimePeriod = xml.find('.//xmlns:aggregationTimePeriod', namespaces={"xmlns" : "http://inspire.ec.europa.eu/schemas/omop/2.9"}).text
        measurements = []
        measurementsElement = member.find(".//wml2:MeasurementTimeseries", namespaces={"wml2" : "http://www.opengis.net/waterml/2.0"})

        for m in measurementsElement:
            measurements.append(self._getOneMeasurement(m))

        return {"label": label, "unit" : unit, "statfunction" : statFunction, "aggregationTimePeriod": aggregationTimePeriod, "measurements" :  measurements }

    def _getOneMeasurement(self, point):
        time = point.find(".//wml2:time", namespaces={"wml2" : "http://www.opengis.net/waterml/2.0"}).text
        value = point.find(".//wml2:value", namespaces={"wml2" : "http://www.opengis.net/waterml/2.0"}).text
        return {"time" : time, "value" : value}



class RequestException(Exception):
    message = "ERROR in date extraction: "

    def __init__(self, text):
        self.details = text

class ToCSV():

    def createCSV(self, parsedData):
        self.openedCsv = open("results.csv", "w", newline='', encoding="utf-8")
        self.csvWriter = csv.writer(self.openedCsv, delimiter=",")
        self._writeHeaders(parsedData)
        self._writeRows(parsedData)

    def _writeHeaders(self, parsedData):
        row = []
        row.append("Time")
        for variable in parsedData["data"]:
            row.append((variable["label"] + " " + variable["unit"]))
        self.csvWriter.writerow(row)

    def _writeRows(self, parsedData):
        print(len(parsedData["data"][0]["measurements"]))
        for i in range(0, len(parsedData["data"][0]["measurements"])):
            row = []
            row.append(parsedData["data"][0]["measurements"][i]["time"])
            for variable in parsedData["data"]:
                row.append(variable["measurements"][i]["value"])
            self.csvWriter.writerow(row)















if __name__ == '__main__':

    query = "/wfs?request=getFeature&storedquery_id=fmi::observations::" \
            "weather::timevaluepair&place=Lammi&timestep=30"
    FMIrequest = FMI_request()

    try:
        dataInXml = FMIrequest.get(query)
        transformer = XmlToClass()
        parsedData = transformer.transform(dataInXml)
        writer = ToCSV()
        writer.createCSV(parsedData)


    except RequestException as e:
        print(e.message)

