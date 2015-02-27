
class RequestException(Exception):
    message = "ERROR in "
    errorCode = 0
    html = ""

    def __init__(self, text, errorCode, html = ""):
        self.message = text
        self.errorCode = errorCode
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