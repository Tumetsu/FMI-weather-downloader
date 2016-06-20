from fmiapi.fmixmlparser import FMIxmlParser
from lxml import etree
from tests.testUtils import *
from tests.fmiapi.testdata.expected_data import *

class TestFMIXmlParserDaily:

    def setup(self):
        self.parser = FMIxmlParser()
        lxmlParser = etree.XMLParser(encoding='utf-8')
        tree = etree.parse('./tests/fmiapi/testdata/daily_12_days.xml', parser=lxmlParser)
        self.test_data1 = tree.getroot()
        tree = etree.parse('./tests/fmiapi/testdata/daily_4_days.xml', parser=lxmlParser)
        self.test_data2 = tree.getroot()
        tree = etree.parse('./tests/fmiapi/testdata/daily_14_days.xml', parser=lxmlParser)
        self.test_data3 = tree.getroot()

    def verify_dataframe(self, given, expected):
        for key, value in expected.items():
            assert given[key] == expected[key], 'dataframe did not match expected'

    def should_parse_xml(self):
        result = self.parser.parse([self.test_data1])
        assertEqual(12, len(result['time']))
        assert 'time' in result
        assert 'rrday' in result
        assert 'tday' in result
        assert 'snow' in result
        assert 'tmin' in result
        assert 'tmax' in result
        assert 'place' in result
        self.verify_dataframe(result, EXPECTED_DAILY_12_DAYS)

    def should_parse_multipart_request_correctly(self):
        result = self.parser.parse([self.test_data1, self.test_data2, self.test_data3])
        assertEqual(30, len(result['time']))

        # concat three different dicts to one df
        expected_df = EXPECTED_DAILY_12_DAYS
        for key in EXPECTED_DAILY_4_DAYS:
            expected_df[key] = expected_df[key] + EXPECTED_DAILY_4_DAYS[key]
        for key in EXPECTED_DAILY_14_DAYS:
            expected_df[key] = expected_df[key] + EXPECTED_DAILY_14_DAYS[key]
        self.verify_dataframe(result, expected_df)


class TestFMIXmlParserRealtime:

    def setup(self):
        self.parser = FMIxmlParser()
        lxmlParser = etree.XMLParser(encoding='utf-8')
        tree = etree.parse('./tests/fmiapi/testdata/realtime_1_day.xml', parser=lxmlParser)
        self.test_data1 = tree.getroot()

    @staticmethod
    def verify_dataframe(given, expected):
        for key, value in expected.items():
            assert given[key] == expected[key], 'dataframe column {}, value {} did not match expected {}'.format(key, value, expected[key])

    def should_parse_xml_and_remove_full_nan_columns(self):
        result = self.parser.parse([self.test_data1])
        assertEqual(153, len(result['time']))
        assert 'time' in result
        assert 't2m' in result
        assert 'rh' in result
        assert 'td' in result
        assert 'snow_aws' in result
        assert 'place' in result
        self.verify_dataframe(result, EXPECTED_REALTIME_1_DAY)
