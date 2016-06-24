
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


class NoDataException(Exception):

    def __init__(self):
        self.message = "ERROR in data-retrieving. Does the server have data for this timespan?"
        self.error_code = "NODATA"

    def __str__(self):
        return self.message
