from fmiapi.fmixmlparser import FMIxmlParser
from lxml import etree
from tests.testUtils import *
from json import dumps

class TestFMIXmlParserSingleList:

    def setup(self):
        self.parser = FMIxmlParser()
        lxmlParser = etree.XMLParser(encoding='utf-8')
        tree = etree.parse('./tests/fmiapi/testdata/daily_12_days.xml', parser=lxmlParser)
        self.test_data1 = tree.getroot()

    def should_parse_xml(self):
        result = self.parser.parse([self.test_data1])
        assertEqual(12, len(result['time']))

    def should_have_all_headers(self):
        result = self.parser.parse([self.test_data1])
        assert 'time' in result
        assert 'rrday' in result
        assert 'tday' in result
        assert 'snow' in result
        assert 'tmin' in result
        assert 'tmax' in result
        assert 'place' in result

        # TODO: Check all datapoints...

    def should_return_empty_list_if_no_data(self):
        pass


class TestFMIXmlParserLongTimeSpans:
    pass
