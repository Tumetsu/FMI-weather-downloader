import csv
import json
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtWidgets import QFileDialog
from gui.messages import Messages
from datetime import datetime


class CsvExport:
    """
    Utility class to export downloaded data to csv file format.
    """
    def __init__(self, app):
        self.app = app

    def save_data_to_csv(self, dataframe, request_params):
        start_date = datetime.strftime(request_params['starttime'], '%Y-%m-%d')
        end_date = datetime.strftime(request_params['endtime'], '%Y-%m-%d')

        paths = QStandardPaths.standardLocations(0)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = ""
        filename = QFileDialog.getSaveFileName(self.app, Messages.save_weatherdata_csv(),
                                               "{}/fmisid-{}_{}_to_{}_weather_data.csv".format(path, request_params['fmisid'], start_date, end_date),
                                               "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._save_to_csv(dataframe, filename[0])

    @staticmethod
    def _save_to_csv(df, path):

        with open(path, 'w', newline='\n') as outfile:
            writer = csv.writer(outfile)
            # Create description rows for measurement units
            with open('data/measurement_descriptions.json', 'r', encoding="utf8") as file:
                descriptions = json.load(file)
                keys = df.keys()
                writer.writerow(['id', 'Label', 'BasePhenomenon', 'Unit', 'AggregationTimePeriod', 'StatisticalFunction'])
                for key in keys:
                    key_lower = key.lower()
                    if key_lower in descriptions:
                        unit = descriptions[key_lower]
                        writer.writerow([unit['id'], unit['label'], unit['basePhenomenon'], unit['uom'], unit['aggregationTimePeriod'], unit['statisticalFunction']])

            writer.writerow([])
            writer.writerow([])
            writer.writerow(keys)
            writer.writerows(zip(*df.values()))
            outfile.close()
