from fmiapi import FMIApi
import datetime
from fmixmlparser import FMIxmlParser, NoDataException

if __name__ == '__main__':
    api = FMIApi()
    api.auth("4d7bcd64-01af-4dbb-8a43-404e97b8c2cd")
    results = api.get_daily_weather( {"request" : "getFeature",
                   "storedquery_id" : "fmi::observations::weather::daily::multipointcoverage",
                   "place" : "Helsinki",
                   "starttime" : datetime.datetime(2015, 1, 1),
                   "endtime" : datetime.datetime(2015, 2, 23)
        })

    try:
        parser = FMIxmlParser()
        alldata = parser.parse(results)
        parser.saveToCsv(alldata, "weather.csv")
    except NoDataException as e:
        print("ERROR: Data saving failed. No data found. Does the service have data for requested timespan?")


