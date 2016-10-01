import csv
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
        startDate = datetime.strftime(request_params['starttime'], '%Y-%m-%d')
        endDate = datetime.strftime(request_params['endtime'], '%Y-%m-%d')

        paths = QStandardPaths.standardLocations(0)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = ""
        filename = QFileDialog.getSaveFileName(self.app, Messages.save_weatherdata_csv(),
                                               "{}/fmisid-{}_{}_to_{}_weather_data.csv".format(path, request_params['fmisid'], startDate, endDate),
                                               "Comma separated values CSV (*.csv);;All files (*)")
        if filename[0] != "":
            self._save_to_csv(dataframe, filename[0])

    @staticmethod
    def _save_to_csv(df, path):
        with open(path, 'w', newline='\n') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(df.keys())
            writer.writerows(zip(*df.values()))
            outfile.close()