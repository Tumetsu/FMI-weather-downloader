
class MockResponse:
    def __init__(self, status, data, content_type='text/xml; charset=UTF8'):
        self.status = status
        self.data = data
        self.content_type = content_type

    def read(self):
        return self.data

    def getheader(self, header):
        if header == 'Content-Type':
            return self.content_type