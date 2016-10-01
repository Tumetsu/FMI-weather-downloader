"""
Utility script to convert FMI's measurement units listings from xml to json. Run only during development to generate json
which is used to retrieve the measurement unit descriptions and added to the resulting data csvs. Xml for input can be retrieved from here:
http://data.fmi.fi/fmi-apikey/<API-KEY>/meta?observableProperty=observation&amp;param=t2m&amp;language=eng
"""
from lxml import etree
import json

_NAMESPACES = {"xmlns": "http://inspire.ec.europa.eu/schemas/omop/2.9",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "gml": "http://www.opengis.net/gml/3.2",
}

with open("measurement_units.xml", "rb") as file:
    data = file.read()
    data = etree.XML(data)

    result = {}
    for item in data:

        uom = item.find(".//xmlns:ObservableProperty/xmlns:uom", namespaces=_NAMESPACES)
        if uom is not None:
            uom = item.find(".//xmlns:ObservableProperty/xmlns:uom", namespaces=_NAMESPACES).attrib['uom']
        else:
            uom = ''

        id = item.find(".//xmlns:ObservableProperty", namespaces=_NAMESPACES).attrib['{http://www.opengis.net/gml/3.2}id']
        result[id] = {
            'label': item.find(".//xmlns:ObservableProperty/xmlns:label", namespaces=_NAMESPACES).text,
            'id': id,
            'uom': uom,
            'basePhenomenon': item.find(".//xmlns:ObservableProperty/xmlns:basePhenomenon", namespaces=_NAMESPACES).text,
            'statisticalFunction': item.find(".//xmlns:statisticalFunction", namespaces=_NAMESPACES).text,
            'aggregationTimePeriod': item.find(".//xmlns:aggregationTimePeriod", namespaces=_NAMESPACES).text,
        }

    with open('measurement_descriptions.json', 'w') as out:
        json.dump(result, out, indent=4, ensure_ascii=False)

