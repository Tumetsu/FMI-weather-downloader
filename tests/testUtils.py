from lxml import etree

def assert_equal(expected, got):
    assert expected == got, "expected {}, got {}".format(expected, got)


def verify_dataframe(given, expected):
    assert_equal(len(given), len(expected))
    for key, value in expected.items():
        assert given[key] == expected[key], 'dataframe did not match expected {} != {}'.format(given[key], expected[key])


def load_xml(path):
    lxml_parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(path, parser=lxml_parser)
    return tree.getroot()


def load_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
        f.close()
    return txt


def create_daily_query(starttime, endtime, fmisid='1234', request='getFeature'):
    return {
        'request': request,
        'storedquery_id': 'fmi::observations::weather::daily::multipointcoverage',
        'fmisid': fmisid,
        'starttime': starttime,
        'endtime': endtime
        }

def create_realtime_query(starttime, endtime, fmisid='1234', request='getFeature'):
    return {
        'request': request,
        'storedquery_id': 'fmi::observations::weather::multipointcoverage',
        'fmisid': fmisid,
        'starttime': starttime,
        'endtime': endtime
        }