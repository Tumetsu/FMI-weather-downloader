
class RequestException(Exception):

    def __init__(self, text, error_code, html=""):
        self.error_code = 0
        self.message = text
        self.error_code = error_code
        self.html = html

    def __str__(self):
        if self.html != "":
            return self.html
        else:
            return self.message


class InvalidApikeyException(Exception):

    def __init__(self):
        self.message = "ERROR in data-retrieving. Your API-key is invalid."
        self.error_code = "APIKEY"

    def __str__(self):
        return self.message


class QueryLimitException(Exception):

    def __init__(self, wait_time=None, wait_unit=None):
        self.message = "ERROR in data-retrieving. Query limit exceeded. Please wait."
        self.error_code = "QUERYLIMIT"
        self.wait_unit = wait_unit
        self.wait_time = wait_time

    def __str__(self):
        return self.message


class NoDataException(Exception):

    def __init__(self, starttime=None, endtime=None):
        self.message = "ERROR in data-retrieving. Did not find any data in range {} - {}".format(starttime, endtime)
        self.error_code = "NODATA"

    def __str__(self):
        return self.message
