import lxml
import http.client
from lxml import etree
class FMI_request():

    url = "data.fmi.fi"
    apikey = "4d7bcd64-01af-4dbb-8a43-404e97b8c2cd"
    headers =  {"Content-type": "text/xml"}
    connection = None

    query1 = "/wfs?request=listStoredQueries"
    query2 = "/wfs?request=getFeature&storedquery_id=fmi::observations::" \
            "weather::timevaluepair&place=Lammi&timestep=30"

    def __init__(self):
        self.connection = http.client.HTTPConnection(self.url)

    def get(self):
        self.connection.request("GET", "/fmi-apikey/" + self.apikey + self.query2,
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

    def transform(self, xmldata):
        pointTimeSeriesObs = xmldata[0].find("omso:PointTimeSeriesObservation", namespaces={"omso" : "http://inspire.ec.europa.eu/schemas/omso/2.0rc3"})


        print(xmldata[0][0])



class WeatherObservations():
    beginTime = ""
    endTime = ""
    locationName = ""

    #data
    wawa = []
    vis = []
    p_sea = []
    snow_aws = []
    ri_10min = []
    r_1h = []
    td = []
    rh = []
    wd_10min = []
    wg_10min = []
    ws_10min = []
    t2m = []



class RequestException(Exception):
    message = "ERROR in date extraction: "

    def __init__(self, text):
        self.details = text



if __name__ == '__main__':
    FMIrequest = FMI_request()

    try:
        dataInXml = FMIrequest.get()
        transformer = XmlToClass()
        transformer.transform(dataInXml)


    except RequestException as e:
        print(e.message)

