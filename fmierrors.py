
class RequestException(Exception):
    message = "ERROR in "
    errorCode = 0
    html = ""

    def __init__(self, text, errorCode, html = ""):
        self.message = text
        self.errorCode = errorCode
        self.html = html
        print(html)


class NoDataException(Exception):
    message = "ERROR with data extraction. Does the server have data for this timespan?"
    errorCode = "NODATA"