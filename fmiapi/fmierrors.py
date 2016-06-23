
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


class NoDataException(Exception):
    message = "ERROR in data-retrieving. Does the server have data for this timespan?"
    errorCode = "NODATA"

    def __str__(self):
        return self.message
