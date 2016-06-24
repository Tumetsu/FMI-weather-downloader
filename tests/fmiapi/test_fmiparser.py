import copy
from fmiapi.fmixmlparser import FMIxmlParser
from tests.testUtils import *
from tests.fmiapi.testdata.expected_data import *

class TestFMIXmlParserDaily:

    def setup(self):
        self.test_data1 = load_xml('./tests/fmiapi/testdata/daily_12_days.xml')
        self.test_data2 = load_xml('./tests/fmiapi/testdata/daily_4_days.xml')
        self.test_data3 = load_xml('./tests/fmiapi/testdata/daily_14_days.xml')
        self.parser = FMIxmlParser()

    def should_parse_xml(self):
        result = self.parser.parse([self.test_data1])
        assert_equal(12, len(result['time']))
        assert 'time' in result
        assert 'rrday' in result
        assert 'tday' in result
        assert 'snow' in result
        assert 'tmin' in result
        assert 'tmax' in result
        assert 'place' in result
        verify_dataframe(result, EXPECTED_DAILY_12_DAYS)

    def should_parse_multipart_request_correctly(self):
        result = self.parser.parse([self.test_data1, self.test_data2, self.test_data3])
        assert_equal(30, len(result['time']))

        # concat three different dicts to one df
        expected_df = copy.deepcopy(EXPECTED_DAILY_12_DAYS)
        for key in EXPECTED_DAILY_4_DAYS:
            expected_df[key] = expected_df[key] + EXPECTED_DAILY_4_DAYS[key]
        for key in EXPECTED_DAILY_14_DAYS:
            expected_df[key] = expected_df[key] + EXPECTED_DAILY_14_DAYS[key]
        verify_dataframe(result, expected_df)


class TestFMIXmlParserRealtime:

    def setup(self):
        self.parser = FMIxmlParser()
        self.test_data1 = load_xml('./tests/fmiapi/testdata/realtime_1_day.xml')

    def should_parse_xml_and_remove_full_nan_columns(self):
        result = self.parser.parse([self.test_data1])
        assert_equal(153, len(result['time']))
        assert 'time' in result
        assert 't2m' in result
        assert 'rh' in result
        assert 'td' in result
        assert 'snow_aws' in result
        assert 'place' in result
        verify_dataframe(result, EXPECTED_REALTIME_1_DAY)
