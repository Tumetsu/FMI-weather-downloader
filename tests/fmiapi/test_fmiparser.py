import copy
from fmiapi.fmixmlparser import FMIxmlParser
from tests.testUtils import *
from tests.fmiapi.testdata.expected_data import *


def describe_fmi_xml_parser():
    parser = FMIxmlParser()

    def describe_daily_data():
        test_data1 = load_xml('./tests/fmiapi/testdata/daily_12_days.xml')
        test_data2 = load_xml('./tests/fmiapi/testdata/daily_4_days.xml')
        test_data3 = load_xml('./tests/fmiapi/testdata/daily_14_days.xml')

        def should_parse_xml():
            result = parser.parse([test_data1])
            assert_equal(12, len(result['time']))
            assert 'time' in result
            assert 'rrday' in result
            assert 'tday' in result
            assert 'snow' in result
            assert 'tmin' in result
            assert 'tmax' in result
            assert 'place' in result
            verify_dataframe(result, EXPECTED_DAILY_12_DAYS)

        def should_parse_multipart_request_correctly():
            result = parser.parse([test_data1, test_data2, test_data3])
            assert_equal(30, len(result['time']))

            # concat three different dicts to one df
            expected_df = copy.deepcopy(EXPECTED_DAILY_12_DAYS)
            for key in EXPECTED_DAILY_4_DAYS:
                expected_df[key] = expected_df[key] + EXPECTED_DAILY_4_DAYS[key]
            for key in EXPECTED_DAILY_14_DAYS:
                expected_df[key] = expected_df[key] + EXPECTED_DAILY_14_DAYS[key]
            verify_dataframe(result, expected_df)

    def describe_realtime_data():
        test_data1 = load_xml('./tests/fmiapi/testdata/realtime_1_day.xml')

        def should_parse_xml_and_remove_full_nan_columns():
            result = parser.parse([test_data1])
            assert_equal(153, len(result['time']))
            assert 'time' in result
            assert 't2m' in result
            assert 'rh' in result
            assert 'td' in result
            assert 'snow_aws' in result
            assert 'place' in result
            verify_dataframe(result, EXPECTED_REALTIME_1_DAY)
